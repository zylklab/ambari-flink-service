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
from resource_management.libraries.script import Script
from resource_management.libraries.functions import get_kinit_path
from resource_management.libraries.functions import default, format
from resource_management.libraries.functions.version import format_stack_version
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions import StackFeature
from ambari_commons import OSCheck

# a map of the Ambari role to the component name
# for use with <stack-root>/current/<component>
SERVER_ROLE_DIRECTORY_MAP = {
  'FLINK' : 'flink'
}

#component_directory = Script.get_component_from_role(SERVER_ROLE_DIRECTORY_MAP, "FLINK_SERVICE")

config = Script.get_config()
stack_root = Script.get_stack_root()
stack_version_unformatted = str(config['clusterLevelParams']['stack_version'])
stack_version_formatted = format_stack_version(stack_version_unformatted)

pid_dir = config['configurations']['flink-env']['flink_pid_dir']
pid_file = format("{pid_dir}/flink.pid")

pid_files = {
  "flink":pid_file
}

# Security related/required params
hostname = config['agentLevelParams']['hostname']
security_enabled = config['configurations']['cluster-env']['security_enabled']
kinit_path_local = get_kinit_path(default('/configurations/kerberos-env/executable_search_paths', None))
tmp_dir = Script.get_tmp_dir()

flink_component_home_dir = "/opt/flink"
conf_dir = "/opt/flink/conf"

flink_user = config['configurations']['flink-env']['flink_user']
flink_ui_principal = default('/configurations/flink-env/flink_principal_name', None)
flink_ui_keytab = default('/configurations/flink-env/flink_keytab', None)

stack_name = default("/clusterLevelParams/stack_name", None)