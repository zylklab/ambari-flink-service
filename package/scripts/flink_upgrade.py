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
import ambari_simplejson as json # simplejson is much faster comparing to Python 2.6 json module and has the same functions set.
import os

from ambari_commons import yaml_utils
from resource_management.core.logger import Logger
from resource_management.core.exceptions import Fail
from resource_management.core.resources.system import Directory
from resource_management.core.resources.system import File
from resource_management.core.resources.system import Execute
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions.format import format

class FlinkUpgrade(Script):
  """
  Applies to Rolling/Express Upgrade from HDP 2.1 or 2.2 to 2.3 or higher.

  Requirements: Needs to run from a host with ZooKeeper Client.

  This class helps perform some of the upgrade tasks needed for Flink during
  a Rolling or Express upgrade. Flink writes data to disk locally and to ZooKeeper.
  If any HDP 2.1 or 2.2 bits exist in these directories when an HDP 2.3 instance
  starts up, it will fail to start properly. Because the upgrade framework in
  Ambari doesn't yet have a mechanism to say "stop all" before starting to
  upgrade each component, we need to rely on a Flink trick to bring down
  running daemons. By removing the ZooKeeper data with running daemons, those
  daemons will die.
  """

if __name__ == "__main__":
  FlinkUpgrade().execute()