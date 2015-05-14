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
from networkapi.equipamento.models import TipoEquipamento
from networkapi.exception import InvalidValueError, BreakLoops
from networkapi.infrastructure.xml_utils import dumps_networkapi, loads
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param, is_valid_version_ip
from networkapi.vlan.models import VlanError, Vlan, VlanNotFoundError
from networkapi.ambiente.models import IP_VERSION, AmbienteNotFoundError
from networkapi.distributedlock import distributedlock, LOCK_VLAN
from networkapi.ambiente.models import Ambiente
from string import split
from networkapi.infrastructure.ipaddr import IPNetwork


class VlanValidateResource(RestResource):

    log = Log('VlanValidateResource')

    def handle_put(self, request, user, *args, **kwargs):
        '''Treat PUT requests to Validate a vlan

        URL: vlan/<id_vlan>/validate/<network>
        '''

        try:

            id_vlan = kwargs.get('id_vlan')

            network = kwargs.get('network')

            # User permission
            if not has_perm(user, AdminPermission.ACL_VLAN_VALIDATION, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Vlan ID
            if not is_valid_int_greater_zero_param(id_vlan):
                self.log.error(
                    u'The id_vlan parameter is not a valid value: %s.', id_vlan)
                raise InvalidValueError(None, 'vlan_id', id_vlan)

            # Valid Network
            if not is_valid_version_ip(network, IP_VERSION):
                self.log.error(
                    u'The network parameter is not a valid value: %s.', network)
                raise InvalidValueError(None, 'network', network)

            # Find Vlan by ID to check if it exist
            vlan = Vlan().get_by_pk(id_vlan)

            with distributedlock(LOCK_VLAN % id_vlan):

                # Set Values
                if network == IP_VERSION.IPv4[0]:
                    vlan.acl_valida = 1

                else:
                    vlan.acl_valida_v6 = 1

                vlan.save(user)

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except VlanNotFoundError, e:
            return self.response_error(116)

        except VlanError, e:
            return self.response_error(1)

    def handle_get(self, request, user, *args, **kwargs):
        '''Treat GET requests to check if a vlan need confimation to insert

        URL: vlan/confirm/
        '''

        try:

            # Get XML data
            ip_version = kwargs.get('ip_version')

            if ip_version == 'None':
                is_number = True
                number = str(kwargs.get('number'))
                id_environment = kwargs.get('id_environment')
            else:
                network = kwargs.get('number')
                network = str(network.replace('net_replace', '/'))
                id_vlan = kwargs.get('id_environment')
                if ip_version == '1':
                    version = 'v6'
                else:
                    version = 'v4'
                is_number = False

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            if is_number:
                # Valid number
                if not is_valid_int_greater_zero_param(id_environment):
                    self.log.error(
                        u'Parameter id_environment is invalid. Value: %s.', id_environment)
                    raise InvalidValueError(
                        None, 'id_environment', id_environment)

                ambiente = Ambiente.get_by_pk(id_environment)

                equips = list()
                envs = list()
                envs_aux = list()

                for env in ambiente.equipamentoambiente_set.all():
                    equips.append(env.equipamento)

                for equip in equips:
                    for env in equip.equipamentoambiente_set.all():
                        if not env.ambiente_id in envs_aux:
                            envs.append(env.ambiente)
                            envs_aux.append(env.ambiente_id)

                # Valid number
                map = dict()
                map['needs_confirmation'] = True

                try:
                    for env in envs:
                        for vlan in env.vlan_set.all():
                            if int(vlan.num_vlan) == int(number):
                                if ambiente.filter_id == None or vlan.ambiente.filter_id == None or int(vlan.ambiente.filter_id) != int(ambiente.filter_id):
                                    map['needs_confirmation'] = False
                                else:
                                    raise BreakLoops()
                except BreakLoops, e:
                    map['needs_confirmation'] = True

            else:

                # Valid subnet
                if not is_valid_int_greater_zero_param(id_vlan):
                    self.log.error(
                        u'Parameter id_vlan is invalid. Value: %s.', id_vlan)
                    raise InvalidValueError(None, 'id_vlan', id_vlan)

                # Get all vlans environments from equipments of the current
                # environment
                vlan = Vlan()
                vlan = vlan.get_by_pk(id_vlan)
                ambiente = vlan.ambiente

                filter = ambiente.filter
                equipment_types = TipoEquipamento.objects.filter(filterequiptype__filter=filter)

                equips = list()
                envs = list()
                envs_aux = list()

                for env in ambiente.equipamentoambiente_set.all().exclude(
                        equipamento__tipo_equipamento__in=equipment_types):
                    equips.append(env.equipamento)

                for equip in equips:
                    for env in equip.equipamentoambiente_set.all():
                        if not env.ambiente_id in envs_aux:
                            envs.append(env.ambiente)
                            envs_aux.append(env.ambiente_id)

                # Check subnet's
                network_ip_verify = IPNetwork(network)

                map = dict()
                map['needs_confirmation'] = False
                try:
                    for env in envs:
                        for vlan_obj in env.vlan_set.all():
                            is_subnet = verify_subnet(vlan_obj, network_ip_verify, version)
                            if is_subnet:
                                raise BreakLoops()
                except BreakLoops, e:
                    map['needs_confirmation'] = True

            # Return XML
            return self.response(dumps_networkapi(map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except Exception, e:
            return self.response_error(1)


def verify_subnet(vlan, network_ip, version):
    if version == IP_VERSION.IPv4[0]:
        vlan_net = vlan.networkipv4_set.all()
    else:
        vlan_net = vlan.networkipv6_set.all()

    # One vlan may have many networks, iterate over it
    for net in vlan_net:

        if version == IP_VERSION.IPv4[0]:
            ip = "%s.%s.%s.%s/%s" % (net.oct1,
                                     net.oct2, net.oct3, net.oct4, net.block)
        else:
            ip = "%s:%s:%s:%s:%s:%s:%s:%s/%d" % (net.block1, net.block2, net.block3,
                                                 net.block4, net.block5, net.block6, net.block7, net.block8, net.block)

        ip_net = IPNetwork(ip)
        # If some network, inside this vlan, is subnet of network search param
        if ip_net in network_ip:
            # This vlan must be in vlans founded, dont need to continue
            # checking
            return True
        # If some network, inside this vlan, is supernet of network search
        # param
        if network_ip in ip_net:
            # This vlan must be in vlans founded, dont need to continue
            # checking
            return True

    # If dont found any subnet return None
    return False
