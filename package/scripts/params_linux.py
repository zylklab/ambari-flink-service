#!/usr/bin/env python
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import os
import re
import ambari_simplejson as json # simplejson is much faster comparing to Python 2.6 json module and has the same functions set.

import status_params

from ambari_commons.constants import AMBARI_SUDO_BINARY
from ambari_commons import yaml_utils
from resource_management.libraries.functions import format
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions.get_bare_principal import get_bare_principal
from resource_management.libraries.script import Script
from resource_management.libraries.resources.hdfs_resource import HdfsResource
from resource_management.libraries.functions import stack_select
from resource_management.libraries.functions import conf_select
from resource_management.libraries.functions import get_kinit_path
from resource_management.libraries.functions.get_not_managed_resources import get_not_managed_resources
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions.stack_features import get_stack_feature_version
from resource_management.libraries.functions import StackFeature
from resource_management.libraries.functions.expect import expect
from resource_management.libraries.functions.setup_atlas_hook import has_atlas_in_cluster
from resource_management.libraries.functions import is_empty
from ambari_commons.ambari_metrics_helper import select_metric_collector_hosts_from_hostnames
from resource_management.libraries.functions.setup_ranger_plugin_xml import get_audit_configs, generate_ranger_service_config

# server configurations
config = Script.get_config()
tmp_dir = Script.get_tmp_dir()
stack_root = status_params.stack_root
sudo = AMBARI_SUDO_BINARY

limits_conf_dir = "/etc/security/limits.d"

# Needed since this is an Atlas Hook service.
cluster_name = config['clusterName']

stack_name = status_params.stack_name
upgrade_direction = default("/commandParams/upgrade_direction", None)
version = default("/commandParams/version", None)

agent_stack_retry_on_unavailability = config['ambariLevelParams']['agent_stack_retry_on_unavailability']
agent_stack_retry_count = expect("/ambariLevelParams/agent_stack_retry_count", int)

flink_component_home_dir = status_params.flink_component_home_dir
conf_dir = status_params.conf_dir

stack_version_unformatted = status_params.stack_version_unformatted
stack_version_formatted = status_params.stack_version_formatted
# get the correct version to use for checking stack features
version_for_stack_feature_checks = get_stack_feature_version(config)

flink_user = config['configurations']['flink-env']['flink_user']
log_dir = config['configurations']['flink-env']['flink_log_dir']
pid_dir = status_params.pid_dir
user_group = config['configurations']['cluster-env']['user_group']
java64_home = config['ambariLevelParams']['java_home']
jps_binary = format("{java64_home}/bin/jps")
security_enabled = config['configurations']['cluster-env']['security_enabled']


if security_enabled:
  _hostname_lowercase = config['agentLevelParams']['hostname'].lower()
  _flink_principal_name = config['configurations']['flink-env']['flink_principal_name']
  flink_jaas_principal = _flink_principal_name.replace('_HOST',_hostname_lowercase)
  _ambari_principal_name = default('/configurations/cluster-env/ambari_principal_name', None)
  flink_keytab_path = config['configurations']['flink-env']['flink_keytab']
  flink_kerberos_keytab = config['configurations']['flink-site']['security.kerberos.login.keytab']
  flink_kerberos_principal = config['configurations']['flink-site']['security.kerberos.login.principal']

  if _ambari_principal_name:
    ambari_bare_jaas_principal = get_bare_principal(_ambari_principal_name)

jdk_location = config['ambariLevelParams']['jdk_location']
namenode_hosts = default("/clusterHostInfo/namenode_hosts", [])
has_namenode = not len(namenode_hosts) == 0

hdfs_user = config['configurations']['hadoop-env']['hdfs_user'] if has_namenode else None
hdfs_user_keytab = config['configurations']['hadoop-env']['hdfs_user_keytab'] if has_namenode else None
hdfs_principal_name = config['configurations']['hadoop-env']['hdfs_principal_name'] if has_namenode else None
hdfs_site = config['configurations']['hdfs-site'] if has_namenode else None
default_fs = config['configurations']['core-site']['fs.defaultFS'] if has_namenode else None
hadoop_bin_dir = stack_select.get_hadoop_dir("bin") if has_namenode else None
hadoop_conf_dir = conf_select.get_hadoop_conf_dir() if has_namenode else None
kinit_path_local = get_kinit_path(default('/configurations/kerberos-env/executable_search_paths', None))
dfs_type = default("/clusterLevelParams/dfs_type", "")


# params from flink-ambari-config
flink_install_dir = "/opt/flink"
flink_bin_dir = "/opt/flink"
flink_numcontainers = config['configurations']['flink-site']['flink_numcontainers']
flink_numberoftaskslots= config['configurations']['flink-site']['flink_numberoftaskslots']
flink_jobmanager_memory = config['configurations']['flink-site']['flink_jobmanager_memory']
flink_container_memory = config['configurations']['flink-site']['flink_container_memory']
flink_appname = config['configurations']['flink-site']['flink_appname']
flink_queue = config['configurations']['flink-site']['flink_queue']
flink_streaming = config['configurations']['flink-site']['flink_streaming']
hadoop_conf_dir = config['configurations']['flink-env']['hadoop_conf_dir']
has_metric_collector = config['configurations']['flink-env']['has_metric_collector']


import functools
#create partial functions with common arguments for every HdfsResource call
#to create/delete hdfs directory/file/copyfromlocal we need to call params.HdfsResource in code
#HdfsResource = functools.partial(
#  HdfsResource,
#  user=hdfs_user,
#  hdfs_resource_ignore_file = "/var/lib/ambari-agent/data/.hdfs_resource_ignore",
#  security_enabled = security_enabled,
#  keytab = hdfs_user_keytab,
#  kinit_path_local = kinit_path_local,
#  hadoop_bin_dir = hadoop_bin_dir,
#  hadoop_conf_dir = hadoop_conf_dir,
#  principal_name = hdfs_principal_name,
#  hdfs_site = hdfs_site,
#  default_fs = default_fs,
#  immutable_paths = get_not_managed_resources(),
#  dfs_type = dfs_type,
#)
