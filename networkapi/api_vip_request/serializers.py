from rest_framework import serializers
from networkapi.requisicaovips.models import VipPortToPool, RequisicaoVips
from networkapi.ambiente.models import Ambiente, EnvironmentVip
from networkapi.exception import EnvironmentVipNotFoundError


class VipPortToPoolSerializer(serializers.ModelSerializer):

    id = serializers.Field()

    requisicao_vip = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True
    )

    class Meta:
        model = VipPortToPool
        fields = (
            'id',
            'requisicao_vip',
            'server_pool',
            'port_vip',
        )


class RequesVipSerializer(serializers.ModelSerializer):

    ip = serializers.PrimaryKeyRelatedField(
        many=False,
        required=False
    )

    ipv6 = serializers.PrimaryKeyRelatedField(
        many=False,
        required=False
    )

    healthcheck_expect = serializers.PrimaryKeyRelatedField(
        many=False,
        required=False
    )

    cliente = serializers.CharField(
        required=False
    )

    rule = serializers.PrimaryKeyRelatedField(
        many=False,
        required=False
    )

    rule_applied = serializers.PrimaryKeyRelatedField(
        many=False,
        required=False
    )

    rule_rollback = serializers.PrimaryKeyRelatedField(
        many=False,
        required=False
    )

    areanegocio = serializers.CharField(
        required=True
    )

    nome_servico = serializers.CharField(
        required=True
    )

    host = serializers.CharField(
        required=True
    )

    vip_ports_to_pools = VipPortToPoolSerializer(
        many=True,
        required=False
    )

    finalidade = serializers.CharField(
        required=True
    )

    cliente = serializers.CharField(
        required=True
    )

    ambiente = serializers.CharField(
        required=True
    )

    def validate(self, attrs):
        """
        Check the Environment Vip is valid.
        """

        try:
            finalidade = attrs.get('finalidade')
            cliente = attrs.get('cliente')
            ambiente = attrs.get('ambiente')

            EnvironmentVip.get_by_values(
                finalidade,
                cliente,
                ambiente
            )

            ip_to_vip = attrs.get('ip') or attrs.get('ipv6')

            if not ip_to_vip:
                raise serializers.ValidationError('Is required to enter any Ip')

        except EnvironmentVipNotFoundError, exception:
            raise serializers.ValidationError(exception.message)

        return attrs

    class Meta:
        model = RequisicaoVips
        depth = 1
        fields = (
            'id', 'ip', 'ipv6', 'l7_filter',
            'filter_applied', 'filter_rollback',
            'filter_valid', 'applied_l7_datetime',
            'healthcheck_expect', 'rule', 'rule_applied',
            'rule_rollback', 'areanegocio', 'nome_servico',
            'host', 'vip_ports_to_pools', 'finalidade',
            'cliente', 'ambiente'
        )


class EnvironmentOptionsSerializer(serializers.ModelSerializer):

    name = serializers.Field()

    class Meta:
        model = Ambiente
        fields = (
            'id',
            'name'
        )
