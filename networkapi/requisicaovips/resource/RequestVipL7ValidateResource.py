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

from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock, LOCK_VIP
from networkapi.equipamento.models import Equipamento, EquipamentoNotFoundError, \
    EquipamentoError
from networkapi.exception import InvalidValueError, \
    EquipmentGroupsNotAuthorizedError, RequestVipsNotBeenCreatedError

from networkapi.infrastructure.script_utils import exec_script, ScriptError
from networkapi.infrastructure.xml_utils import dumps_networkapi, XMLError, loads

from networkapi.log import Log
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param, \
    is_valid_int_greater_equal_zero_param, clone
from networkapi.ambiente.models import EnvironmentVip


class RequestVipL7ValidateResource(RestResource):

    log = Log('RequestVipL7ValidateResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Validate L7 filter

        URLs: /vip/l7/<id_vip>/validate/
        """
        try:

            if not has_perm(user,
                            AdminPermission.VIP_VALIDATION,
                            AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            self.log.info("Validate L7 filter to VIP")

            id_vip = kwargs.get('id_vip')

            # Valid Vip ID
            if not is_valid_int_greater_zero_param(id_vip):
                self.log.error(
                    u'The vip_id parameter is not a valid value: %s.', id_vip)
                raise InvalidValueError(None)

            vip = RequisicaoVips.get_by_pk(id_vip)

            with distributedlock(LOCK_VIP % id_vip):

                # Vip must be created
                if not vip.vip_criado:
                    self.log.error(
                        u'L7 filter can not be changed because VIP has not yet been created.')
                    raise RequestVipsNotBeenCreatedError(None)

                vip.filter_valid = True

                vip.save(user)

                map = dict()
                map['sucesso'] = 'sucesso'
                return self.response(dumps_networkapi(map))

        except UserNotAuthorizedError:
            return self.not_authorized()
