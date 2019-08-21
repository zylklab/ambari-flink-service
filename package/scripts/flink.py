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

from resource_management.core.exceptions import Fail
from resource_management.core.resources.service import ServiceConfig
from resource_management.core.resources.system import Directory, Execute, File, Link
from resource_management.core.source import Template, InlineTemplate
from resource_management.libraries.resources.template_config import TemplateConfig
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions.format import format
from resource_management.libraries.script.script import Script
from resource_management.core.source import Template
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions import StackFeature
from flink_yaml_utils import yaml_config_template
from ambari_commons.os_family_impl import OsFamilyFuncImpl, OsFamilyImpl
from ambari_commons import OSConst
from resource_management.libraries.functions.generate_logfeeder_input_config import generate_logfeeder_input_config
from resource_management.libraries.functions.setup_atlas_hook import has_atlas_in_cluster, setup_atlas_hook, setup_atlas_jar_symlinks
from ambari_commons.constants import SERVICE


@OsFamilyFuncImpl(os_family=OsFamilyImpl.DEFAULT)
def flink(name=None):
  import params
  import os

  Directory(params.log_dir,
            owner=params.flink_user,
            group=params.user_group,
            mode=0777,
            create_parents = True,
            cd_access="a",
  )

  Directory([params.pid_dir],
            owner=params.flink_user,
            group=params.user_group,
            create_parents = True,
            cd_access="a",
            mode=0755,
  )

  
  configurations = params.config['configurations']['flink-site']

  File(format("{conf_dir}/flink-conf.yaml"),
       content=yaml_config_template(configurations),
       owner=params.flink_user,
       group=params.user_group
  )

  generate_logfeeder_input_config('flink', Template("input.config-flink.json.j2", extra_imports=[default]))

  if params.has_metric_collector:
    File(format("{conf_dir}/flink-metrics2.properties"),
        owner=params.flink_user,
        group=params.user_group,
        content=Template("flink-metrics2.properties.j2")
    )

  if params.security_enabled:
    TemplateConfig(format("{conf_dir}/flink_jaas.conf"),
                   owner=params.flink_user,
                   mode=0644
    )
    if params.stack_version_formatted and check_stack_feature(StackFeature.ROLLING_UPGRADE, params.stack_version_formatted):
      TemplateConfig(format("{conf_dir}/client_jaas.conf"),
                     owner=params.flink_user,
                     mode=0644
      )
  else:
    File(
      format("{conf_dir}/flink_jaas.conf"),
      action="delete"
    )
    File(
      format("{conf_dir}/client_jaas.conf"),
      action="delete"
    )


def _find_real_user_min_uid():
  """
  Finds minimal real user UID
  """
  with open('/etc/login.defs') as f:
    for line in f:
      if line.strip().startswith('UID_MIN') and len(line.split()) == 2 and line.split()[1].isdigit():
        return int(line.split()[1])
  raise Fail("Unable to find UID_MIN in file /etc/login.defs. Expecting format e.g.: 'UID_MIN    500'")  
