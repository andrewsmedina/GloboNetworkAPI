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

from django.db.transaction import commit_on_success
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from networkapi.log import Log
from networkapi.api_vip_request.permissions import Read, Write
from networkapi.requisicaovips.models import ServerPool, VipPortToPool, \
    RequisicaoVips, RequisicaoVipsError
from networkapi.error_message_utils import error_messages
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_pools import exceptions as pool_exceptions
from networkapi.api_vip_request import exceptions
from networkapi.ambiente.models import EnvironmentVip, Ambiente, EnvironmentEnvironmentVip
from networkapi.api_vip_request.serializers import EnvironmentOptionsSerializer
from networkapi.exception import InvalidValueError, EnvironmentVipNotFoundError
from networkapi.api_vip_request import facade


log = Log(__name__)


class DuplicatedVipPortException(Exception):
    """
    Duplicated port for VipPortPool
    """
    pass

@api_view(['POST'])
@permission_classes((IsAuthenticated, Read))
@commit_on_success
def add_pools(request):
    """
    Add Pools For Vip Request.
    """
    try:
        pool_ids = request.DATA.get('pool_ids')
        vip_request_id = request.DATA.get('vip_request_id')

        vip_request_obj = RequisicaoVips.objects.get(id=vip_request_id)

        for pool_id in pool_ids:

            pool_obj = ServerPool.objects.get(id=pool_id)

            # verificar se o Ambiente de cada IP do Pool é
            # igual ao Ambiente vinculado ao AmbienteVIP da RequisicaoVIP

            server_pool_member_list = pool_obj.serverpoolmember_set.all()
            variable_map = vip_request_obj.variables_to_map()
            environment_vip = EnvironmentVip.get_by_values(variable_map.get('finalidade'),
                                                           variable_map.get('cliente'),
                                                           variable_map.get('ambiente'))

            ipv4_list = [obj for obj in server_pool_member_list if obj.ip]
            ipv6_list = set(server_pool_member_list) - set(ipv4_list)

            ipv4_list = [obj.ip for obj in ipv4_list]
            ipv6_list = [obj.ipv6 for obj in ipv6_list]

            if VipPortToPool.objects.filter(port_vip=pool_obj.default_port, requisicao_vip=vip_request_obj).count() > 0:
                raise DuplicatedVipPortException(
                    error_messages.get(397) % (pool_obj.default_port, vip_request_obj.id))

            for ipv4 in ipv4_list:
                environment = ipv4.networkipv4.vlan.ambiente

                if not EnvironmentEnvironmentVip.environment_is_related_to_environment_vip(environment.id,
                                                                                           environment_vip.id):
                    raise api_exceptions.EnvironmentEnvironmentVipNotBoundedException(
                        error_messages.get(398) % (environment.name, ipv4.ip_formated, environment_vip.name)
                    )

            for ipv6 in ipv6_list:
                environment = ipv6.networkipv6.vlan.ambiente

                if not EnvironmentEnvironmentVip.environment_is_related_to_environment_vip(environment.id,
                                                                                           environment_vip.id):
                    raise api_exceptions.EnvironmentEnvironmentVipNotBoundedException(
                        error_messages.get(398) % (pool_obj.environment.name, ipv6.ip_formated, environment_vip.name)
                )

            vip_port_pool_obj = VipPortToPool(
                requisicao_vip=vip_request_obj,
                server_pool=pool_obj,
                port_vip=pool_obj.default_port
            )

            vip_port_pool_obj.save(request.user)

        return Response(status=status.HTTP_201_CREATED)

    except RequisicaoVips.DoesNotExist, exception:
        log.error(exception)
        raise exceptions.VipRequestDoesNotExistException()

    except ServerPool.DoesNotExist, exception:
        log.error(exception)
        raise pool_exceptions.PoolDoesNotExistException()

    except DuplicatedVipPortException, exception:
        log.error(exception)
        raise exceptions.DuplicatedVipPortForVipRequestPoolException()

    except api_exceptions.EnvironmentEnvironmentVipNotBoundedException, exception:
        log.error(exception)
        raise api_exceptions.EnvironmentEnvironmentVipNotBoundedException()

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST'])
@permission_classes((IsAuthenticated, Write))
@commit_on_success
def delete(request):
    """
    Delete Vip Request And Optional Related Pools.
    """
    try:
        ids = request.DATA.get('ids')
        delete_pools = request.DATA.get('delete_pools', True)

        if delete_pools:
            vports_pool = VipPortToPool.objects.filter(
                requisicao_vip__id__in=ids
            )

            for vport in vports_pool:

                server_pool = vport.server_pool

                related = VipPortToPool.objects.filter(
                    server_pool=server_pool
                ).exclude(
                    requisicao_vip=vport.requisicao_vip
                )

                if related:
                    raise pool_exceptions.PoolConstraintVipException()

                vport.delete(request.user)

                for member in server_pool.serverpoolmember_set.all():
                    member.delete(request.user)

                server_pool.delete(request.user)

        vips_request = RequisicaoVips.objects.filter(id__in=ids)
        for vrequest in vips_request:
            vrequest.delete(request.user)

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
@commit_on_success
def list_environment_by_environment_vip(request, environment_vip_id):

    try:

        env_vip = EnvironmentVip.objects.get(id=environment_vip_id)

        environment_query = Ambiente.objects.filter(
            Q(vlan__networkipv4__ambient_vip=env_vip) |
            Q(vlan__networkipv6__ambient_vip=env_vip)
        ).distinct()

        serializer_environment = EnvironmentOptionsSerializer(
            environment_query,
            many=True
        )

        return Response(serializer_environment.data)

    except EnvironmentVip.DoesNotExist, exception:
        log.error(exception)
        raise api_exceptions.ObjectDoesNotExistException('Environment Vip Does Not Exist')

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST', 'PUT'])
@permission_classes((IsAuthenticated, Write))
@commit_on_success
def save(request, pk=None):

    try:

        if request.method == "POST":

            data = facade.save(request)

            return Response(data=data, status=status.HTTP_201_CREATED)

        elif request.method == "PUT":

            data = facade.update(request, pk)

            return Response(data=data)

    except EnvironmentVipNotFoundError, error:
        log.error(error)
        raise exceptions.EnvironmentVipDoesNotExistException()

    except exceptions.InvalidIdVipRequestException, exception:
        log.error(exception)
        raise exception

    except RequisicaoVips.DoesNotExist, exception:
        log.error(exception)
        raise exceptions.VipRequestDoesNotExistException()

    except (InvalidValueError, RequisicaoVipsError, api_exceptions.ValidationException), exception:
        log.error(exception)
        raise api_exceptions.ValidationException()

    except api_exceptions.EnvironmentEnvironmentVipNotBoundedException, exception:
        log.error(exception)
        raise exception

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
@commit_on_success
def get_by_pk(request, pk):

    try:

        data = facade.get_by_pk(pk)

        return Response(data)

    except exceptions.InvalidIdVipRequestException, exception:
        log.error(exception)
        raise exception

    except RequisicaoVips.DoesNotExist, exception:
        log.error(exception)
        raise exceptions.VipRequestDoesNotExistException()

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()
