from django.db import models

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


from networkapi.log import Log

from networkapi.models.BaseModel import BaseModel
from networkapi.ambiente.models import Ambiente
from networkapi.requisicaovips.models import RequisicaoVips


class Rule(BaseModel):

    id = models.AutoField(primary_key=True, db_column='id_rule')
    environment = models.ForeignKey(
        Ambiente, db_column='id_ambiente', null=False)
    name = models.CharField(
        max_length=80, blank=False, null=False, db_column='name')
    vip = models.ForeignKey(
        RequisicaoVips, db_column='id_vip', null=True, related_name='vip')

    log = Log('Rule')

    class Meta (BaseModel.Meta):
        managed = True
        db_table = u'rule'


class BlockRules(BaseModel):

    id = models.AutoField(primary_key=True, db_column='id_block_rules')
    content = models.TextField(blank=False, null=False, db_column='content')
    environment = models.ForeignKey(
        Ambiente, db_column='id_ambiente', null=False)
    order = models.IntegerField(null=False, blank=False)

    log = Log('BlockRules')

    class Meta (BaseModel.Meta):
        db_table = u'block_rules'
        managed = True


class RuleContent(BaseModel):

    id = models.AutoField(primary_key=True, db_column='id_rule_content')
    content = models.TextField(blank=False, null=False, db_column='content')
    order = models.IntegerField(null=False, blank=False, db_column='order')
    rule = models.ForeignKey(
        Rule, null=False, db_column='id_rule', on_delete=models.CASCADE)

    log = Log('RuleContent')

    class Meta (BaseModel.Meta):
        managed = True
        db_table = u'rule_content'
