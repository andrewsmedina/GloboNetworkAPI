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


from django.db import models

from networkapi.ambiente.models import Ambiente

from networkapi.grupo.models import EGrupo

from networkapi.tipoacesso.models import TipoAcesso

from networkapi.roteiro.models import Roteiro

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from networkapi.log import Log

from networkapi.models.BaseModel import BaseModel

from _mysql_exceptions import OperationalError


class EquipamentoError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com Equipamento."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class EquipamentoNotFoundError(EquipamentoError):

    """Retorna exceção para pesquisa de equipamento por chave primária."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class EquipamentoGrupoNotFoundError(EquipamentoError):

    """Retorna exceção para pesquisa de equipamento_grupo por chave primária."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class EquipamentoAmbienteNotFoundError(EquipamentoError):

    """Retorna exceção para pesquisa de equipamento_ambiente por chave primária ou equipamento e ambiente."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class EquipTypeCantBeChangedError(EquipamentoError):

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class EquipamentoRoteiroNotFoundError(EquipamentoError):

    """Retorna exceção para pesquisa de equipamento_roteiro."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class EquipamentoRoteiroDuplicatedError(EquipamentoError):

    """Retorna exceção quando o equipamento_roteiro já existe."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class EquipamentoGrupoDuplicatedError(EquipamentoError):

    """Retorna exceção quando o equipamento_grupo já existe."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class EquipamentoAmbienteDuplicatedError(EquipamentoError):

    """Retorna exceção quando o equipamento_ambiente já existe."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class TipoEquipamentoNotFoundError(EquipamentoError):

    """Retorna exceção para pesquisa de tipo de equipamento por chave primária."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class ModeloNotFoundError(EquipamentoError):

    """Retorna exceção para pesquisa de modelo de equipamento por chave primária."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class MarcaNotFoundError(EquipamentoError):

    """Retorna exceção para pesquisa de modelo de equipamento por chave primária."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class InvalidGroupToEquipmentTypeError(EquipamentoError):

    """Equipamento do grupo “Equipamentos Orquestração” somente poderá ser criado com tipo igual a “Servidor Virtual”."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class EquipamentoNameDuplicatedError(EquipamentoError):

    """Retorna exceção porque já existe um Equipamento cadastrado com o mesmo nome."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class EquipamentoAccessDuplicatedError(EquipamentoError):

    """Retorna exceção porque já existe um Equipamento cadastrado com o mesmo nome."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class EquipamentoAccessNotFoundError(EquipamentoError):

    """Retorna exceção para pesquisa de modelo de equipamento por chave primária."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class EquipmentDontRemoveError(EquipamentoError):

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class MarcaUsedByModeloError(EquipamentoError):

    """Retorna exceção se houver tentativa de exclusão de marca utilizada por algum modelo."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class MarcaModeloNameDuplicatedError(EquipamentoError):

    """Retorna exceção se houver um Modelo e Marca com mesmo nome já cadastrado.."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class ModeloUsedByEquipamentoError(EquipamentoError):

    """Retorna exceção se houver tentativa de exclusão de um modelo utilizado por algum equipamento."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class MarcaNameDuplicatedError(EquipamentoError):

    """Retorna exceção porque já existe uma marca cadastrado com o mesmo nome."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class TipoEquipamentoDuplicateNameError(EquipamentoError):

    """Retorna exceção porque já existe um tipo de equipamento cadastrado com o mesmo nome."""

    def __init__(self, cause, message=None):
        EquipamentoError.__init__(self, cause, message)


class Marca(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_marca')
    nome = models.CharField(max_length=100)

    log = Log('Marca')

    class Meta(BaseModel.Meta):
        db_table = u'marcas'
        managed = True

    """
    @classmethod
    def search(cls):
        try:
            return Marca.objects.all()
        except Exception:
            cls.log.error(u'Falha ao pesquisar as marcas de equipamentos.')
            raise EquipamentoError(u'Falha ao pesquisar as marcas de equipamentos.')
        
    def create(self, authenticated_user):
        try:
            Marca.get_by_name(self.nome)
            raise MarcaNameDuplicatedError(None, u'Marca com o nome %s já cadastrada.' % self.nome)
        except MarcaNotFoundError:
            pass
        
        try:
            self.save(authenticated_user)
        except Exception:
            self.log.error(u'Falha ao inserir marca de equipamento.')
            raise EquipamentoError(u'Falha ao inserir marca de equipamento.')

        
    @classmethod
    def update(cls, authenticated_user, pk, **kwargs):
        brand = Marca.get_by_pk(pk)
        
        try:
            name = kwargs['nome']
            if brand.nome.lower() != name.lower():
                Marca.get_by_name(name)
                raise MarcaNameDuplicatedError(None, u'Marca com o nome %s já cadastrada.' % name)
        except (KeyError, MarcaNotFoundError):
            pass
        
        try:
            brand.__dict__.update(kwargs)
            brand.save(authenticated_user)
        except Exception, e:
            cls.log.error(u'Falha ao atualizar a marca de equipamento.')
            raise EquipamentoError(e, u'Falha ao atualizar a marca de equipamento.')   
    
    @classmethod 
    def remove(cls, authenticated_user, pk):
        brand = Marca.get_by_pk(pk)
        
        try:
            if brand.modelo_set.count() > 0:
                raise MarcaUsedByModeloError(None, u"A marca %d tem modelo associado." % brand.id)

            brand.delete(authenticated_user)
        except MarcaUsedByModeloError, e:
            raise e
        except Exception, e:
            cls.log.error(u'Falha ao remover a marca de equipamento.')
            raise EquipamentoError(e, u'Falha ao remover a marca de equipamento.')
    """

    @classmethod
    def get_by_pk(cls, idt):
        """"Get  Brand id.

        @return: Brand L3.

        @raise MarcaNotFoundError: Brand is not registered.
        @raise EquipamentoError: Failed to search for the Brand.
        """
        try:
            return Marca.objects.filter(id=idt).uniqueResult()
        except ObjectDoesNotExist, e:
            raise MarcaNotFoundError(
                e, u'Dont there is a Brand by pk = %s.' % idt)
        except Exception, e:
            cls.log.error(u'Failure to search the Brand.')
            raise EquipamentoError(e, u'Failure to search the Brand.')

    @classmethod
    def get_by_name(cls, name):
        """"Get Brand by name.

        @return: Brand.

        @raise MarcaNotFoundError: Brand is not registered.
        @raise EquipamentoError: Failed to search for the Brand.
        """
        try:
            return Marca.objects.get(nome__iexact=name)
        except ObjectDoesNotExist, e:
            raise MarcaNotFoundError(
                e, u'Dont there is a Brand by name = %s.' % name)
        except Exception, e:
            cls.log.error(u'Failure to search the Brand.')
            raise EquipamentoError(e, u'Failure to search the Brand.')


class Modelo(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_modelo')
    nome = models.CharField(max_length=100)
    marca = models.ForeignKey(Marca, db_column='id_marca')

    log = Log('Modelo')

    class Meta(BaseModel.Meta):
        db_table = u'modelos'
        managed = True

    @classmethod
    def get_by_pk(cls, idt):
        """"Get Model by id.

        @return: Model.

        @raise RoteiroNotFoundError: Model is not registered.
        @raise EquipamentoError: Failed to search for the Model.
        """
        try:
            return Modelo.objects.filter(id=idt).uniqueResult()
        except ObjectDoesNotExist, e:
            raise ModeloNotFoundError(
                e, u'Dont there is a Model by pk = %s.' % idt)
        except Exception, e:
            cls.log.error(u'Failure to search the Model.')
            raise EquipamentoError(e, u'Failure to search the Model.')

    @classmethod
    def get_by_name(cls, name):
        """"Get Model by name.

        @return: Model.

        @raise ModeloNotFoundError: Model is not registered.
        @raise EquipamentoError: Failed to search for the Model.
        """
        try:
            return Modelo.objects.get(nome__iexact=name)
        except ObjectDoesNotExist, e:
            raise ModeloNotFoundError(
                e, u'Dont there is a Model by name = %s.' % name)
        except Exception, e:
            cls.log.error(u'Failure to search the Model.')
            raise EquipamentoError(e, u'Failure to search the Model.')

    @classmethod
    def get_by_name_brand(cls, name, id_brand):
        """"Get Model by Name and Brand.

        @return: Model.

        @raise ModeloNotFoundError: Model is not registered.
        @raise EquipamentoError: Failed to search for the Model.
        """
        try:
            return Modelo.objects.get(nome__iexact=name, marca__id=id_brand)
        except ObjectDoesNotExist, e:
            raise ModeloNotFoundError(
                e, u'Dont there is a Model by name = %s and Brand = %s.' % (name, id_brand))
        except Exception, e:
            cls.log.error(u'Failure to search the Model.')
            raise EquipamentoError(e, u'Failure to search the Model.')

    @classmethod
    def get_by_brand(cls, id_brand):
        """"Get Model by Brand.

        @return: Model.

        @raise ModeloNotFoundError: Model is not registered.
        @raise EquipamentoError: Failed to search for the Model.
        """
        try:
            return Modelo.objects.filter(marca__id=id_brand)
        except ObjectDoesNotExist, e:
            raise ModeloNotFoundError(
                e, u'Dont there is a Model by Brand = %s.' % id_brand)
        except Exception, e:
            cls.log.error(u'Failure to search the Model.')
            raise EquipamentoError(e, u'Failure to search the Model.')


class TipoEquipamento(BaseModel):
    TIPO_EQUIPAMENTO_SERVIDOR_VIRTUAL = 10
    TIPO_EQUIPAMENTO_SWITCH = 1
    TIPO_EQUIPAMENTO_ROUTER = 3

    id = models.AutoField(primary_key=True, db_column='id_tipo_equipamento')
    tipo_equipamento = models.CharField(max_length=100)

    log = Log('TipoEquipamento')

    class Meta(BaseModel.Meta):
        db_table = u'tipo_equipamento'
        managed = True

    @classmethod
    def get_by_pk(self, idt):
        """"Get Equipment Type by id.

        @return: Equipment Type.

        @raise TipoEquipamentoNotFoundError: Equipment Type is not registered.
        @raise EquipamentoError: Failed to search for the Equipment Type.
        """
        try:
            return TipoEquipamento.objects.filter(id=idt).uniqueResult()
        except ObjectDoesNotExist, e:
            raise TipoEquipamentoNotFoundError(
                e, u'Dont there is a Equipment Type by pk = %s.' % idt)
        except Exception, e:
            self.log.error(u'Failure to search the Equipment Type.')
            raise EquipamentoError(e, u'Failure to search the Equipment Type.')

    @classmethod
    def get_tipo(self, tipo):
        """"Get Equipment Type by Type.

        @return: Equipment Type.

        @raise TipoEquipamentoNotFoundError: Equipment Type is not registered.
        @raise EquipamentoError: Failed to search for the Equipment Type.
        """
        try:
            return TipoEquipamento.objects.get(tipo_equipamento=tipo)
        except ObjectDoesNotExist, e:
            raise TipoEquipamentoNotFoundError(
                e, u'Dont there is a Equipment Type by type = %s.' % tipo)
        except Exception, e:
            self.log.error(u'Failure to search the Equipment Type.')
            raise EquipamentoError(e, u'Failure to search the Equipment Type.')

    @classmethod
    def get_tipo_balanceador(self):
        """"Get Equipment Type by Type is balanceador.

        @return: Equipment Type.

        @raise TipoEquipamentoNotFoundError: Equipment Type is not registered.
        @raise EquipamentoError: Failed to search for the Equipment Type.
        """
        try:
            return TipoEquipamento.objects.get(tipo_equipamento__iexact="balanceador")
        except ObjectDoesNotExist, e:
            raise TipoEquipamentoNotFoundError(
                e, u'Dont there is a Equipment Type by type is balanceador.')
        except Exception, e:
            self.log.error(u'Failure to search the Equipment Type.')
            raise EquipamentoError(e, u'Failure to search the Equipment Type.')

    @classmethod
    def get_by_name(cls, name):
        """"Get Equipment Type by name.

        @return: Equipment Type.

        @raise ModeloNotFoundError: Equipment Type is not registered.
        @raise EquipamentoError: Failed to search for the Equipment Type.
        """
        try:
            return Modelo.objects.get(nome__iexact=name)
        except ObjectDoesNotExist, e:
            raise TipoEquipamentoNotFoundError(
                e, u'Dont there is a Equipment Type by name = %s.' % name)
        except Exception, e:
            cls.log.error(u'Failure to search the Equipment Type.')
            raise EquipamentoError(e, u'Failure to search the Equipment Type.')

    def search(self):
        try:
            return TipoEquipamento.objects.all()
        except Exception, e:
            self.log.error(u'Falha ao pesquisar os tipos de equipamentos.')
            raise EquipamentoError(
                e, u'Falha ao pesquisar os tipos de equipamentos.')

    def insert_new(self, authenticated_user, name):
        try:

            try:

                TipoEquipamento.objects.get(tipo_equipamento__iexact=name)
                raise TipoEquipamentoDuplicateNameError(
                    None, u'Tipo equipamento %s, já cadastrado' % (name))
            except ObjectDoesNotExist, e:
                pass

            self.tipo_equipamento = name
            self.save(authenticated_user)
            return self.id

        except TipoEquipamentoDuplicateNameError, e:
            self.log.error(e.message)
            raise TipoEquipamentoDuplicateNameError(e, e.message)
        except Exception, e:
            self.log.error(u'Falha ao inserir tipo de equipamentos.')
            raise EquipamentoError(
                e, u'Falha ao inserir tipo de equipamentos.')


class Equipamento(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_equip')
    tipo_equipamento = models.ForeignKey(
        TipoEquipamento, db_column='id_tipo_equipamento')
    modelo = models.ForeignKey(Modelo, db_column='id_modelo')
    nome = models.CharField(unique=True, max_length=50)
    grupos = models.ManyToManyField(EGrupo, through='EquipamentoGrupo')
    maintenance = models.BooleanField(db_column='maintenance')

    log = Log('Equipamento')

    class Meta(BaseModel.Meta):
        db_table = u'equipamentos'
        managed = True

    @classmethod
    def get_next_name_by_prefix(cls, prefix):
        try:
            names = Equipamento.objects.filter(
                nome__istartswith=prefix).values_list('nome', flat=True).distinct()
            if len(names) == 0:
                return '%s%d' % (prefix, 1)

            # obtem a lista somente com os números da parte numérica dos nomes
            start_value = len(prefix)
            values = [int(name[start_value:]) for name in names]

            # ordena a lista
            values.sort()

            # obtem o maior número
            last_value = values[len(values) - 1]

            # busca um número não utilizado entre 1 e o maior número da lista
            for i in range(1, last_value + 1):
                if i not in values:
                    return '%s%d' % (prefix, i)

            # retorna o ultimo valor da lista + 1
            return '%s%d' % (prefix, last_value + 1)
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar os equipamentos.')
            raise EquipamentoError(e, u'Falha ao pesquisar os equipamentos.')

    def create(self, authenticated_user, group_id):
        '''Insere um novo Equipamento

        Se o grupo do equipamento, informado nos dados da requisição, for igual à “Equipamentos Orquestracao” (id = 1) 
        então o tipo do equipamento deverá ser igual a “Servidor Virtual” (id = 10).

        @return: Nothing

        @raise InvalidGroupToEquipmentTypeError: Equipamento do grupo “Equipamentos Orquestração” somente poderá ser criado com tipo igual a “Servidor Virtual”.

        @raise EGrupoNotFoundError: Grupo não cadastrado. 

        @raise GrupoError: Falha ao pesquisar o Grupo. 

        @raise TipoEquipamentoNotFoundError: Tipo de equipamento nao cadastrado.

        @raise ModeloNotFoundError: Modelo nao cadastrado.

        @raise EquipamentoNameDuplicatedError: Nome do equipamento duplicado.

        @raise EquipamentoError: Falha ou inserir o equipamento. 
        '''
        if self.nome is not None:
            self.nome = self.nome.upper()

        egroup = EGrupo.get_by_pk(group_id)

        if group_id == EGrupo.GRUPO_EQUIPAMENTO_ORQUESTRACAO and self.tipo_equipamento.id != TipoEquipamento.TIPO_EQUIPAMENTO_SERVIDOR_VIRTUAL:
            raise InvalidGroupToEquipmentTypeError(
                None, u'Equipamento do grupo “Equipamentos Orquestração” somente poderá ser criado com tipo igual a “Servidor Virtual”.')

        self.tipo_equipamento = TipoEquipamento().get_by_pk(
            self.tipo_equipamento.id)

        self.modelo = Modelo.get_by_pk(self.modelo.id)

        if self.maintenance is None:
            self.maintenance = False

        try:
            self.get_by_name(self.nome)
            raise EquipamentoNameDuplicatedError(
                None, u'Equipamento com nome duplicado.')
        except EquipamentoNotFoundError:
            self.log.debug('Equipamento com o mesmo nome não encontrado.')

        try:
            self.save(authenticated_user)

            equipment_group = EquipamentoGrupo()
            equipment_group.egrupo = egroup
            equipment_group.equipamento = self
            equipment_group.save(authenticated_user)

            return equipment_group.id
        except Exception, e:
            self.log.error(u'Falha ao inserir o equipamento.')
            raise EquipamentoError(e, u'Falha ao inserir o equipamento.')

    @classmethod
    def get_by_pk(cls, pk):
        """Get Equipament by id.

            @return: Equipament.

            @raise EquipamentoNotFoundError: Equipament is not registered.
            @raise EquipamentoError: Failed to search for the Equipament.
            @raise OperationalError: Lock wait timeout exceeded. 
        """
        try:
            return Equipamento.objects.filter(id=pk).uniqueResult()
        except ObjectDoesNotExist, e:
            raise EquipamentoNotFoundError(
                e, u'Dont there is a equipament by pk = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the equipament.')
            raise EquipamentoError(e, u'Failure to search the equipament.')

    def edit(self, user, nome, tipo_equip, modelo):
        try:
            self.modelo = modelo
            self.tipo_equipamento = tipo_equip
            self.nome = nome
            self.save(user)
        except EquipamentoNameDuplicatedError, e:
            raise EquipamentoNameDuplicatedError(e.message)
        except Exception, e:
            self.log.error(u'Falha ao editar o equipamento.')
            raise EquipamentoError(e, u'Falha ao editar o equipamento.')

    @classmethod
    def get_by_name(cls, name):
        try:
            return Equipamento.objects.get(nome__iexact=name)
        except ObjectDoesNotExist, e:
            raise EquipamentoNotFoundError(
                e, u'Não existe um equipamento com o nome = %s.' % name)
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar o equipamento.')
            raise EquipamentoError(e, u'Falha ao pesquisar o equipamento.')

    def search(self, equip_name=None, equip_type_id=None, environment_id=None, ugroups=None):
        try:
            equips = Equipamento.objects.all()

            if ugroups is not None:
                equips = equips.filter(
                    grupos__direitosgrupoequipamento__ugrupo__in=ugroups, grupos__direitosgrupoequipamento__leitura='1')

            if equip_name is not None:
                equips = equips.filter(nome__iexact=equip_name)

            if equip_type_id is not None:
                equips = equips.filter(tipo_equipamento__id=equip_type_id)

            if environment_id is not None:
                equips = equips.filter(
                    equipamentoambiente__ambiente__id=environment_id)

            return equips
        except Exception, e:
            self.log.error(u'Falha ao pesquisar os equipamentos.')
            raise EquipamentoError(e, u'Falha ao pesquisar os equipamentos.')

    def delete(self, authenticated_user):
        '''Sobrescreve o metodo do Django para remover um equipamento.

        Antes de remover o equipamento remove todos os seus relacionamentos.
        '''
        from networkapi.ip.models import IpCantBeRemovedFromVip

        is_error = False
        ipv4_error = ""
        ipv6_error = ""

        for ip_equipment in self.ipequipamento_set.all():
            try:
                ip = ip_equipment.ip
                ip_equipment.delete(authenticated_user)
            except Exception, e:
                is_error = True
                ipv4_error += " %s.%s.%s.%s - Vip %s ," % (
                    ip.oct1, ip.oct2, ip.oct3, ip.oct4, e.cause)

        for ip_v6_equipment in self.ipv6equipament_set.all():

            try:
                ip = ip_v6_equipment.ip
                ip_v6_equipment.delete(authenticated_user)
            except Exception, e:
                is_error = True
                ipv6_error += " %s:%s:%s:%s:%s:%s:%s:%s - Vip %s ," % (
                    ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8, e.cause)

        if is_error:
            raise IpCantBeRemovedFromVip(ipv4_error, ipv6_error)

        for equipment_access in self.equipamentoacesso_set.all():
            equipment_access.delete(authenticated_user)

        for equipment_script in self.equipamentoroteiro_set.all():
            equipment_script.delete(authenticated_user)

        for interface in self.interface_set.all():
            interface.delete(authenticated_user)

        for equipment_environment in self.equipamentoambiente_set.all():
            equipment_environment.delete(authenticated_user)

        for equipment_group in self.equipamentogrupo_set.all():
            equipment_group.delete(authenticated_user)

        super(Equipamento, self).delete(authenticated_user)

    def remove(self, authenticated_user, equip_id):
        '''Pesquisa e remove o equipamento.

        @return: Nothing

        @raise EquipamentoNotFoundError: Não existe um equipamento com equip_id .

        @raise EquipamentoError: Falha ao remover o equipamento.
        '''
        from networkapi.ip.models import IpCantBeRemovedFromVip

        equipment = self.get_by_pk(equip_id)
        try:
            equipment.delete(authenticated_user)
        except IpCantBeRemovedFromVip, e:
            raise e
        except Exception, e:
            self.log.error(u'Falha ao remover um equipamento.')
            raise EquipamentoError(e, u'Falha ao remover um equipamento.')


class EquipamentoAmbiente(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_equip_do_ambiente')
    ambiente = models.ForeignKey(Ambiente, db_column='id_ambiente')
    equipamento = models.ForeignKey(Equipamento, db_column='id_equip')
    is_router = models.BooleanField(db_column='is_router')

    log = Log('EquipamentoAmbiente')

    class Meta(BaseModel.Meta):
        db_table = u'equip_do_ambiente'
        managed = True
        unique_together = ('equipamento', 'ambiente')

    def create(self, authenticated_user):
        '''Insere uma nova associação entre um Equipamento e um Ambiente.

        @return: Nothing

        @raise AmbienteNotFoundError: Ambiente não cadastrado.

        @raise EquipamentoAmbienteDuplicatedError: Equipamento já está cadastrado no Ambiente.

        @raise EquipamentoError: Falha ao inserir a associação Equipamento e Ambiente.
        '''

        self.ambiente = Ambiente().get_by_pk(self.ambiente.id)
        self.equipamento = Equipamento().get_by_pk(self.equipamento.id)

        try:
            exist = EquipamentoAmbiente().get_by_equipment_environment(
                self.equipamento.id, self.ambiente.id)
            raise EquipamentoAmbienteDuplicatedError(
                None, u'Equipamento já está cadastrado no ambiente.')
        except EquipamentoAmbienteNotFoundError:
            pass

        try:
            self.save(authenticated_user)
        except Exception, e:
            self.log.error(u'Falha ao inserir a associação equipamento/ambiente: %s/%s.' %
                           (self.equipamento.id, self.ambiente.id))
            raise EquipamentoError(
                e, u'Falha ao inserir a associação equipamento/ambiente: %s/%s.' % (self.equipamento.id, self.ambiente.id))

    def get_by_equipment_environment(self, equipment_id, environment_id):
        try:
            return EquipamentoAmbiente.objects.get(ambiente__id=environment_id, equipamento__id=equipment_id)
        except ObjectDoesNotExist, e:
            raise EquipamentoAmbienteNotFoundError(
                e, u'Não existe um equipamento_ambiente com o equipamento = %s e o ambiente = %s.' % (equipment_id, environment_id))
        except Exception, e:
            self.log.error(u'Falha ao pesquisar o equipamento-ambiente.')
            raise EquipamentoError(
                e, u'Falha ao pesquisar o equipamento-ambiente.')

    @classmethod
    def get_by_equipment(self, equipment_id):
        try:
            return EquipamentoAmbiente.objects.filter(equipamento__id=equipment_id)
        except ObjectDoesNotExist, e:
            raise EquipamentoAmbienteNotFoundError(
                e, u'Não existe um equipamento_ambiente com o equipamento = %s.' % equipment_id)
        except Exception, e:
            self.log.error(u'Falha ao pesquisar o equipamento-ambiente.')
            raise EquipamentoError(
                e, u'Falha ao pesquisar o equipamento-ambiente.')

    @classmethod
    def remove(cls, authenticated_user, equip_id, environ_id):
        '''Pesquisa e remove uma associação entre um Equipamento e um Ambiente.

        @return: Nothing

        @raise EquipamentoAmbienteNotFoundError: Não existe associação entre o equipamento e o ambiente.

        @raise EquipamentoError: Falha ao remover uma associação entre um Equipamento e um Ambiente.
        '''

        try:
            equipenvironment = EquipamentoAmbiente.objects.get(
                equipamento__id=equip_id, ambiente__id=environ_id)
            equipenvironment.delete(authenticated_user)

        except ObjectDoesNotExist, n:
            cls.log.error(u'Não existe um equipamento_ambiente com o equipamento = %s e o ambiente = %s.' % (
                equip_id, environ_id))
            raise EquipamentoAmbienteNotFoundError(
                n, u'Não existe um equipamento_ambiente com o equipamento = %s e o ambiente = %s.' % (equip_id, environ_id))
        except Exception, e:
            cls.log.error(
                u'Falha ao remover uma associação entre um Equipamento e um Ambiente.')
            raise EquipamentoError(
                e, u'Falha ao remover uma associação entre um Equipamento e um Ambiente.')


class EquipamentoGrupo(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_equip_do_grupo')
    egrupo = models.ForeignKey(EGrupo, db_column='id_egrupo')
    equipamento = models.ForeignKey(Equipamento, db_column='id_equip')

    log = Log('EquipamentoGrupo')

    class Meta(BaseModel.Meta):
        db_table = u'equip_do_grupo'
        managed = True
        unique_together = ('egrupo', 'equipamento')

    def create(self, authenticated_user):
        '''Insere uma nova associação entre um Equipamento e um Grupo.

        @return: Nothing

        @raise EGrupoNotFoundError: Grupo não cadastrado.

        @raise GrupoError: Falha ao pesquisar o grupo do equipamento.  

        @raise EquipamentoGrupoDuplicatedError: Equipamento já está cadastrado no grupo

        @raise EquipamentoError: Falha ao inserir o equipamento no grupo.
        '''

        self.egrupo = EGrupo.get_by_pk(self.egrupo.id)
        self.equipamento = Equipamento().get_by_pk(self.equipamento.id)

        try:
            self.get_by_equipment_group(self.equipamento.id, self.egrupo.id)
            raise EquipamentoGrupoDuplicatedError(
                None, u'Equipamento já está cadastrado no grupo.')
        except EquipamentoGrupoNotFoundError:
            pass

        try:
            self.save(authenticated_user)
        except Exception, e:
            self.log.error(u'Falha ao inserir a associação equipamento/grupo: %d/%d.' %
                           (self.equipamento.id, self.egrupo.id))
            raise EquipamentoError(
                e, u'Falha ao inserir a associação equipamento/grupo: %d/%d.' % (self.equipamento.id, self.egrupo.id))

    @classmethod
    def get_by_equipment(self, equipment_id):
        try:
            return EquipamentoGrupo.objects.filter(equipamento__id=equipment_id)
        except ObjectDoesNotExist, e:
            raise EquipamentoGrupoNotFoundError(
                e, u'Não existe um equipamento_grupo com o equipamento = %s ' % (equipment_id))
        except Exception, e:
            self.log.error(u'Falha ao pesquisar o equipamento-grupo.')
            raise EquipamentoError(
                e, u'Falha ao pesquisar o equipamento-grupo.')

    def get_by_equipment_group(self, equipment_id, egroup_id):
        try:
            return EquipamentoGrupo.objects.get(egrupo__id=egroup_id, equipamento__id=equipment_id)
        except ObjectDoesNotExist, e:
            raise EquipamentoGrupoNotFoundError(
                e, u'Não existe um equipamento_grupo com o equipamento = %s e o grupo = %s.' % (equipment_id, egroup_id))
        except Exception, e:
            self.log.error(u'Falha ao pesquisar o equipamento-grupo.')
            raise EquipamentoError(
                e, u'Falha ao pesquisar o equipamento-grupo.')

    @classmethod
    def remove(cls, authenticated_user, equip_id, egroup_id):
        '''Pesquisa e remove uma associação entre um Equipamento e um Grupo.

        @return: Nothing

        @raise EquipamentoGrupoNotFoundError: Associação entre o equipamento e o grupo não cadastrada.

        @raise EquipamentoError: Falha ao remover uma associação entre um Equipamento e um Grupo.
        '''
        equip_group = EquipamentoGrupo().get_by_equipment_group(
            equip_id, egroup_id)

        equipments = EquipamentoGrupo.get_by_equipment(equip_id)

        if len(equipments) > 1:
            try:
                equip_group.delete(authenticated_user)
            except Exception, e:
                cls.log.error(
                    u'Falha ao remover uma associação entre um Equipamento e um Grupo.')
                raise EquipamentoError(
                    e, u'Falha ao remover uma associação entre um Equipamento e um Grupo.')
        else:
            raise EquipmentDontRemoveError(
                u'Failure to remove an association between an equipment and a group because the group is related only to a group.')


class EquipamentoAcesso(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_equiptos_access')
    equipamento = models.ForeignKey(Equipamento, db_column='id_equip')
    fqdn = models.CharField(max_length=100)
    user = models.CharField(max_length=20)
    # Field renamed because it was a Python reserved word. Field name made
    # lowercase.
    password = models.CharField(max_length=20, db_column='pass')
    tipo_acesso = models.ForeignKey(TipoAcesso, db_column='id_tipo_acesso')
    enable_pass = models.CharField(max_length=20, blank=True)

    log = Log('EquipamentoAcesso')

    class Meta(BaseModel.Meta):
        db_table = u'equiptos_access'
        managed = True
        unique_together = ('equipamento', 'tipo_acesso')

    @classmethod
    def get_by_pk(self, id):
        '''Get EquipamentoAcesso by id.

        @return: EquipamentoAcesso.

        @raise EquipamentoAccessNotFoundError: EquipamentoAcesso is not registered.
        @raise VlanError: Failed to search for the EquipamentoAcesso.
        @raise OperationalError: Lock wait timeout exceed
        '''
        try:
            return EquipamentoAcesso.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise EquipamentoAccessNotFoundError(
                e, u'Dont there is a EquipamentoAcesso by pk = %s.' % id)
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the EquipamentoAcesso.')
            raise EquipamentoError(
                e, u'Failure to search the EquipamentoAcesso.')

    @classmethod
    def search(cls, ugroups=None):
        """Efetua a pesquisa das informações de acesso a equipamentos
        @return: Um queryset contendo as informações de aceso a equipamentos cadastrados
        @raise EquipamentoError: Falha ao pesquisar as informações de acesso a equipamentos.
        """
        try:
            results = EquipamentoAcesso.objects.all()
            if ugroups is not None:
                results = results.filter(
                    equipamento__grupos__direitosgrupoequipamento__ugrupo__in=ugroups, equipamento__grupos__direitosgrupoequipamento__escrita='1')
            return results
        except Exception, e:
            cls.log.error(
                u'Falha ao pesquisar as informações de acesso a equipamentos.')
            raise EquipamentoError(
                e, u'Falha ao pesquisar oas informações de acesso a equipamentos.')

    def create(self, authenticated_user):
        """Efetua a inclusão de informações de acesso a equipamentos
        @return: Instância da informação de acesso a equipamento incluída
        @raise Equipamento.DoesNotExist: Equipamento informado é inexistente
        @raise TipoAcesso.DoesNotExist: Tipo de acesso informado é inexistente
        @raise EquipamentoAccessDuplicatedError: Já existe cadastrada a associação de equipamento e tipo de acesso informada
        @raise EquipamentoError: Falha ao incluir informações de acesso a equipamentos.
        """
        # Valida a existência do equipamento
        self.equipamento = Equipamento.get_by_pk(self.equipamento.id)
        try:
            # Valida a existência do tipo de acesso
            self.tipo_acesso = TipoAcesso.objects.get(id=self.tipo_acesso.id)

            # Verifica a existência de uma associação de equipamento e tipo de acesso igual à que está
            # sendo incluída
            if EquipamentoAcesso.objects.filter(equipamento=self.equipamento, tipo_acesso=self.tipo_acesso).count() > 0:
                raise EquipamentoAccessDuplicatedError(
                    None, u'Já existe esta associação de equipamento e tipo de acesso cadastrada.')

            # Persiste a informação
            return self.save(authenticated_user)

        except TipoAcesso.DoesNotExist, e:
            raise e
        except EquipamentoAccessDuplicatedError, e:
            raise e
        except Exception, e:
            self.log.error(
                u'Falha ao inserir informação de acesso a equipamento.')
            raise EquipamentoError(
                e, u'Falha ao inserir informação de acesso a equipamento.')

    @classmethod
    def update(cls, authenticated_user, id_equipamento, id_tipo_acesso, **kwargs):
        """Efetua a alteração de informações de acesso a equipamentos conforme argumentos recebidos
        @param id_equipamento: Identificador do equipamento da informação de acesso a equipamento a ser alterada 
        @param id_tipo_acesso: Identificador do tipo de acesso da informação de acesso a equipamento a ser alterada 
        @return: Instância da informação de acesso a equipamento alterada
        @raise EquipamentoAcesso.DoesNotExist: Informação de acesso a equipamento informada é inexistente
        @raise EquipamentoError: Falha ao alterar informação de acesso a equipamento.
        """

        try:
            # Obtém a informação de acesso a equipamento a ser alterada
            equipamento_acesso = EquipamentoAcesso.objects.get(
                equipamento__id=id_equipamento, tipo_acesso__id=id_tipo_acesso)

            # Bind dos valores recebidos para o objeto a ser alterado
            equipamento_acesso.__dict__.update(kwargs)

            # Persiste a informação
            return equipamento_acesso.save(authenticated_user)

        except EquipamentoAcesso.DoesNotExist, e:
            raise e
        except Exception, e:
            cls.log.error(
                u'Falha ao alterar informação de acesso a equipamento.')
            raise EquipamentoError(
                e, u'Falha ao alterar informação de acesso a equipamento.')

    @classmethod
    def remove(cls, authenticated_user, id_equipamento, id_tipo_acesso):
        """Efetua a remoção de um tipo de acesso
        @param id_equipamento: Identificador do equipamento da informação de acesso a equipamento a ser excluída 
        @param id_tipo_acesso: Identificador do tipo de acesso da informação de acesso a equipamento a ser excluída 
        @return: nothing
        @raise EquipamentoAcesso.DoesNotExist: Informação de acesso a equipamento informada é inexistente
        @raise EquipamentoError: Falha ao alterar informação de acesso a equipamento.
        """
        try:
            # Obtém a informação de acesso a equipamento a ser excluída
            equipamento_acesso = EquipamentoAcesso.objects.get(
                equipamento__id=id_equipamento, tipo_acesso__id=id_tipo_acesso)

            return equipamento_acesso.delete(authenticated_user)

        except EquipamentoAcesso.DoesNotExist, e:
            raise e
        except Exception, e:
            EquipamentoAcesso.log.error(
                u'Falha ao excluir informação de acesso a equipamento.')
            raise EquipamentoError(
                e, u'Falha ao excluir informação de acesso a equipamento.')


class EquipamentoRoteiro(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_equiptos_roteiros')
    equipamento = models.ForeignKey(Equipamento, db_column='id_equip')
    roteiro = models.ForeignKey(Roteiro, db_column='id_roteiros')

    log = Log('EquipamentoRoteiro')

    class Meta(BaseModel.Meta):
        db_table = u'equiptos_roteiros'
        managed = True
        unique_together = ('equipamento', 'roteiro')

    @classmethod
    def search(cls, ugroups=None, equip_id=None):
        try:
            er = EquipamentoRoteiro.objects.all()

            if ugroups is not None:
                er = er.filter(equipamento__grupos__direitosgrupoequipamento__ugrupo__in=ugroups,
                               equipamento__grupos__direitosgrupoequipamento__leitura='1')

            if equip_id is not None:
                er = er.filter(equipamento__id=equip_id)

            return er

        except Exception, e:
            cls.log.error(
                u'Falha ao pesquisar os equipamentos e roteiros associados.')
            raise EquipamentoError(
                e, u'Falha ao pesquisar os equipamentos e roteiros associados.')

    def create(self, authenticated_user):
        '''Insere uma nova associação entre um Equipamento e um Roteiro.

        @return: Nothing

        @raise RoteiroNotFoundError: Roteiro não cadastrado.

        @raise RoteiroError: Falha ao pesquisar o roteiro.  

        @raise EquipamentoRoteiroDuplicatedError: Equipamento já está associado ao roteiro.

        @raise EquipamentoError: Falha ao inserir o equipamento no roteiro.
        '''
        self.equipamento = Equipamento().get_by_pk(self.equipamento.id)
        self.roteiro = Roteiro.get_by_pk(self.roteiro.id)

        try:
            try:
                EquipamentoRoteiro.objects.get(
                    equipamento__id=self.equipamento.id, roteiro__id=self.roteiro.id)
                raise EquipamentoRoteiroDuplicatedError(
                    None, u'Equipamento já está associado ao roteiro.')
            except ObjectDoesNotExist:
                pass

            self.save(authenticated_user)
        except EquipamentoRoteiroDuplicatedError, e:
            raise e
        except Exception, e:
            self.log.error(u'Falha ao inserir a associação equipamento/roteiro: %s/%s.' %
                           (self.equipamento.id, self.roteiro.id))
            raise EquipamentoError(
                e, u'Falha ao inserir a associação equipamento/roteiro: %s/%s.' % (self.equipamento.id, self.roteiro.id))

    @classmethod
    def remove(cls, authenticated_user, equip_id, script_id):
        '''Pesquisa e remove uma associação entre um Equipamento e um Roteiro.

        @return: Nothing

        @raise EquipamentoRoteiroNotFoundError: Não existe associação entre o equipamento e o roteiro.

        @raise EquipamentoError: Falha ao remover uma associação entre um Equipamento e um Roteiro.
        '''
        try:
            equip_script = EquipamentoRoteiro.objects.get(
                equipamento__id=equip_id, roteiro__id=script_id)
            equip_script.delete(authenticated_user)

        except EquipamentoRoteiro.DoesNotExist, n:
            cls.log.debug(u'Não existe um equipamento_roteiro com o equipamento = %s e o roteiro = %s.' % (
                equip_id, script_id))
            raise EquipamentoRoteiroNotFoundError(
                n, u'Não existe um equipamento_roteiro com o equipamento = %s e o roteiro = %s.' % (equip_id, script_id))
        except Exception, e:
            cls.log.error(
                u'Falha ao remover uma associação entre um Equipamento e um Roteiro.')
            raise EquipamentoError(
                e, u'Falha ao remover uma associação entre um Equipamento e um Roteiro.')
