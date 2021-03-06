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

from networkapi.auth import has_perm
from networkapi.admin_permission import AdminPermission
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.exception import InvalidValueError
from networkapi.ambiente.models import AmbienteError, Ambiente
from networkapi.rest import RestResource


class EnvironmentGetAclPathsResource(RestResource):

    def handle_get(self, request, user, *args, **kwargs):
        '''Handles a get request to a environment lookup.

        Lists all distinct ACL paths

        URL: /environment/acl_path/ 
        '''
        try:
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()

            acl_paths = list(Ambiente.objects.values_list(
                'acl_path', flat=True).distinct().exclude(acl_path=None))

            return self.response(dumps_networkapi({'acl_paths': acl_paths}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except (AmbienteError):
            return self.response_error(1)
