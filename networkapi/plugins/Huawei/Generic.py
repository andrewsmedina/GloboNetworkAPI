# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.plugins import exceptions as base_exceptions
from networkapi.log import Log
from ..base import BasePlugin

log = Log(__name__)

class Generic(BasePlugin):

	VALID_TFTP_GET_MESSAGE = 'Copy complete, now saving to disk'

	def copyScriptFileToConfig (self, filename, use_vrf=None, destination="running-config"):
		
		if use_vrf == None:
			use_vrf = self.management_vrf

		command = 'tftp %s get %s %s' % (self.tftpserver,filename, vpn_instance)
		log.info("sending command: %s" % command)

		self.channel.send("%s\n" % command)
		recv = self.waitString(self.VALID_TFTP_PUT_MESSAGE)

		local_filename = re.split('\/', filename)[-1]

		command = 'execute %s' % (local_filename)
		log.info("sending command: %s" % command)

		self.channel.send("%s\n" % command)
		recv += self.waitString(self.VALID_TFTP_PUT_MESSAGE)

		return recv
