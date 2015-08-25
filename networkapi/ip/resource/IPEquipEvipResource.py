# -*- coding: utf-8 -*-

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
from networkapi.ambiente.models import EnvironmentVip, EnvironmentEnvironmentVip
from networkapi.auth import has_perm
from networkapi.equipamento.models import EquipamentoNotFoundError, EquipamentoError, Equipamento
from networkapi.exception import InvalidValueError, EnvironmentVipNotFoundError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.ip.models import NetworkIPv4NotFoundError, IpError, NetworkIPv4Error, IpNotFoundByEquipAndVipError
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param, is_valid_string_maxsize, is_valid_string_minsize, is_valid_regex


class IPEquipEvipResource(RestResource):

    log = Log('IPEquipEvipResource')

    def handle_post(self, request, user, *args, **kwargs):
        """
        Return the IPs (v4 and/or v6) that can be balanced.
        URL: ip/getbyequipandevip/

        @param request: a POST request
        @param user: the user that makes the request
        @param args: arguments
        @param kwargs: keyword arguments

        @return: {"ipv4": list_ipsv4, "ipv6": list_ipsv6}

        @raise IpNotFoundByEquipAndVipError: IP is not related equipment and Environment Vip.
        @raise InvalidValueError: An error occurred validating a value.
        @raise NetworkIPv4NotFoundError: Network ipv4 not found.
        @raise EquipamentoNotFoundError: Equipamento not found.
        @raise EnvironmentVipNotFoundError: Environment vip not found.
        @raise UserNotAuthorizedError: User is not authorized.
        @raise XMLError: Failed to read XML.
        @raise IpError: Failed to search for the IP.
        @raise NetworkIPv4Error: An error related to networkipv4.
        @raise EquipamentoError: Failed to search for the Equipamento.
        @raise GrupoError: Failed to search for the Grupo.
        """

        self.log.info('Get Ips by Equip - Evip')

        try:

            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.READ_OPERATION):
                raise UserNotAuthorizedError(
                    None, u'User does not have permission to perform the operation.')

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            ip_map = networkapi_map.get('ip_map')
            if ip_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            id_evip = ip_map.get('id_evip')
            equip_name = ip_map.get('equip_name')

            # Valid id_evip
            if not is_valid_int_greater_zero_param(id_evip):
                self.log.error(
                    u'Parameter id_evip is invalid. Value: %s.', id_evip)
                raise InvalidValueError(None, 'id_evip', id_evip)

            # Valid equip_name
            if not is_valid_string_minsize(equip_name, 3) or not is_valid_string_maxsize(equip_name, 80) or not is_valid_regex(equip_name, "^[A-Z0-9-_]+$"):
                self.log.error(
                    u'Parameter equip_name is invalid. Value: %s', equip_name)
                raise InvalidValueError(None, 'equip_name', equip_name)

            # Business Rules

            # Get Environment VIp
            evip = EnvironmentVip.get_by_pk(id_evip)

            # n-n relationship between environment and environment vip
            envs = EnvironmentEnvironmentVip.get_environment_list_by_environment_vip(evip)

            # Get Equipment
            equip = Equipamento.get_by_name(equip_name)

            lista_ips_equip = set()
            lista_ipsv6_equip = set()

            # Get all IPV4's Equipment
            for ipequip in equip.ipequipamento_set.select_related().all():
                if ipequip.ip.networkipv4.vlan.ambiente in envs:
                    lista_ips_equip.add(ipequip.ip)

            # Get all IPV6'S Equipment
            for ipequip in equip.ipv6equipament_set.select_related().all():
                if ipequip.ip.networkipv6.vlan.ambiente in envs:
                    lista_ipsv6_equip.add(ipequip.ip)

            # lists and dicts to return
            ipsv4 = []
            ipsv6 = []

            for ip in lista_ips_equip:
                ipv4 = {'id': ip.id,
                        'ip': "{0}.{1}.{2}.{3}".format(ip.oct1, ip.oct2, ip.oct3, ip.oct4),
                        'network': {
                            'network': "{0}.{1}.{2}.{3}".format(ip.networkipv4.oct1, ip.networkipv4.oct2,
                                                                ip.networkipv4.oct3, ip.networkipv4.oct4),
                            'mask': "{0}.{1}.{2}.{3}".format(ip.networkipv4.mask_oct1, ip.networkipv4.mask_oct2,
                                                             ip.networkipv4.mask_oct3, ip.networkipv4.mask_oct4)
                        }
                }

                ipsv4.append(ipv4)

            ipv6_mask = "{0}:{1}:{2}:{3}:{4}:{5}:{6}:{7}:{8}"

            for ip in lista_ipsv6_equip:
                ipv6 = {'id': ip.id,
                        'ip': ipv6_mask.format(ip.block1, ip.block2, ip.block3, ip.block4,
                                               ip.block5, ip.block6, ip.block7, ip.block8),
                        'network': {
                            'network': ipv6_mask.format(ip.networkipv6.block1, ip.networkipv6.block2,
                                                        ip.networkipv6.block3, ip.networkipv6.block4,
                                                        ip.networkipv6.block5, ip.networkipv6.block6,
                                                        ip.networkipv6.block7, ip.networkipv6.block8),
                            'mask': ipv6_mask.format(ip.networkipv6.block1, ip.networkipv6.block2,
                                                     ip.networkipv6.block3, ip.networkipv6.block4,
                                                     ip.networkipv6.block5, ip.networkipv6.block6,
                                                     ip.networkipv6.block7, ip.networkipv6.block8)
                        }
                }

                ipsv6.append(ipv6)

            if not ipsv4 and not ipsv6:
                raise IpNotFoundByEquipAndVipError(
                    None, 'Ip nao encontrado com equipamento %s e ambiente vip %s' % (equip_name, id_evip))

            resp = dumps_networkapi({"ipv4": ipsv4, "ipv6": ipsv6})
            return self.response(resp)

        except IpNotFoundByEquipAndVipError:
            return self.response_error(317, equip_name, id_evip)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv4NotFoundError:
            return self.response_error(281)
        except EquipamentoNotFoundError:
            return self.response_error(117, ip_map.get('id_equipment'))
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except (IpError, NetworkIPv4Error, EquipamentoError, GrupoError), e:
            self.log.error(e)
            return self.response_error(1)
