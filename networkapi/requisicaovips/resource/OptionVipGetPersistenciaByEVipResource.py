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


from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.exception import OptionVipError, EnvironmentVipError, EnvironmentVipNotFoundError, InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.requisicaovips.models import OptionVip


class OptionVipGetPersistenciaByEVipResource(RestResource):

    log = Log('OptionVipGetTimeoutByEVipResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all persistencia of the Option VIP by Environment Vip. 

        URL: environment-vip/get/persitencia/<id_evip>
        """

        try:

            self.log.info("GET to list all the Option VIP by Environment Vip.")

            # User permission
            if not has_perm(user, AdminPermission.OPTION_VIP, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_environment_vip = kwargs.get('id_evip')

            # Valid Environment VIP ID
            if not is_valid_int_greater_zero_param(id_environment_vip):
                self.log.error(
                    u'The id_environment_vip parameter is not a valid value: %s.', id_environment_vip)
                raise InvalidValueError(
                    None, 'id_environment_vip', id_environment_vip)

            # Find Environment VIP by ID to check if it exist
            environment_vip = EnvironmentVip.get_by_pk(id_environment_vip)

            ovips = OptionVip.get_all_persistencia(environment_vip.id)

            ovip_dict = dict()
            ovip_list = []

            for ovip in ovips:
                ovip_dict['persistencia_opt'] = ovip.nome_opcao_txt
                ovip_list.append(ovip_dict)
                ovip_dict = dict()

            return self.response(dumps_networkapi({'persistencia_opt': ovip_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except EnvironmentVipNotFoundError:
            return self.response_error(283)

        except OptionVipError, EnvironmentVipError:
            return self.response_error(1)
