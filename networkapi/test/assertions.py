# encoding: utf-8

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

from networkapi.test.utils import xml2dict, log


def assert_response_error(response, codigo, descricao=None):
    """ Verifica se a resposta da networkapi foi como esperada. Quando for passado uma lista de códigos
        possiveis, a descrição não poderá ser passada
    """

    # trata o argumento código, quando somente 1 elemento for passado
    codigos = codigo if type(codigo) == list else [codigo]
    try:
        networkapi_response = xml2dict(response.content)
        codigo_resposta = int(networkapi_response['erro']['codigo'])
        descricao_resposta = networkapi_response['erro']['descricao']
        assert codigo_resposta in codigos, u"Código de resposta inválido: %d (descricao: %s). Esperados: %s" % (
            codigo_resposta, descricao_resposta, repr(codigos))
        assert descricao_resposta != None
        assert len(descricao_resposta) > 0
        if descricao:
            assert descricao_resposta == descricao
    except:
        # Se houver algum erro na formação (parsing) da resposta, imprimo qual
        # ela era para facilitar a investigação
        log.error("Erro fazendo parsing da resposta:\n%s\n",
                  (response or response.content))
        raise


def assert_response_success(response, status_code=200, codigo=0, stdout=None, stderr=None):
    """ Verifica se a resposta da networkapi foi sucesso e com os valores informados """
    try:
        assert response.status_code == status_code
        networkapi_response = xml2dict(response.content)
        codigo_resposta = int(networkapi_response['sucesso']['codigo'])
        assert codigo_resposta == codigo, u"Código de resposta inválido: %d. Esperado: %d" % (
            codigo_resposta, codigo)

        if stdout:
            assert networkapi_response['sucesso'][
                'descricao']['stdout'] == stdout

        if stderr:
            assert networkapi_response['sucesso'][
                'descricao']['stderr'] == stderr
    except:
        # Se houver algum erro na formação (parsing) da resposta, imprimo qual
        # ela era para facilitar a investigação
        log.error("Erro fazendo parsing da resposta:\n%s\n",
                  (response or response.content))
        raise
