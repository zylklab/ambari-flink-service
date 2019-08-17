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

import sys, os, pwd, grp, signal, time, glob, subprocess
from resource_management.libraries.functions import check_process_status
from resource_management.core.logger import Logger
from resource_management.libraries.script import Script
from resource_management.libraries.functions import stack_select
from resource_management.libraries.functions import format
from resource_management.core.resources.system import Execute
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions import StackFeature
from resource_management.core.resources.system import Directory, Execute, File, Link
from flink import flink
from service import service
from service_check import ServiceCheck
from resource_management.libraries.functions.security_commons import build_expectations, \
  cached_kinit_executor, get_params_from_filesystem, validate_security_config_properties, \
  FILE_TYPE_JAAS_CONF

class FlinkServer(Script):

  def install(self, env):
	Logger.info('********************************')
	Logger.info('* Installing Flink on the node *')
	Logger.info('********************************')
	import status_params
	import params
	env.set_params(status_params)
	env.set_params(params)
	Logger.info('*****status_params********************pid_dir: '+status_params.pid_dir)
	Logger.info('*****params**********flink_component_home_dir: '+params.flink_component_home_dir)
	Logger.info('*****params***************************log_dir: '+params.log_dir)
	Logger.info('*****params************************flink_user: '+params.flink_user)
	Logger.info('*****params************************user_group: '+params.user_group)

	service_packagedir = os.path.realpath(__file__).split('/scripts')[0]
	Logger.info('***************************service_packagedir: '+service_packagedir)
	
	cmd = 'tar -xvzf '+service_packagedir+'/files/flink-bin-1.8.1/flink.tar.gz --strip-components=1 -C /opt/flink'
	Logger.info('******************************************cmd: '+cmd)
	Directory([status_params.pid_dir, params.log_dir, params.flink_component_home_dir],
            owner=params.flink_user,
            group=params.user_group
    )
	Execute(cmd, user=params.flink_user)
	self.configure(env)
	
  def configure(self, env):
    import params
    env.set_params(params)
    flink()

  def pre_upgrade_restart(self, env, upgrade_type=None):
    import params
    env.set_params(params)
    if params.version and check_stack_feature(StackFeature.ROLLING_UPGRADE, params.version):
      stack_select.select_packages(params.version)

  def start(self, env, upgrade_type=None):
	import params
	env.set_params(params)
	self.configure(env)
	service("flink", action="start")

  def stop(self, env, upgrade_type=None):
	import params
	env.set_params(params)
	service("flink", action="stop")

  def status(self, env):
	import status_params
	env.set_params(status_params)
	check_process_status(status_params.pid_file)
      
  def get_log_folder(self):
	import params  
	return params.log_dir
  
  def get_user(self):
	import params
	return params.flink_user

  def get_pid_files(self):
	import status_params
	return [status_params.pid_file]

if __name__ == "__main__":
  FlinkServer().execute()
