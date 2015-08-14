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
from networkapi.log import Log

class QueueMessage(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_queue_message')
    message = models.TextField(null=False, blank=False, db_column='message')
    queue = models.CharField(null=False, blank=False, max_length=250, db_column='queue')
    sent = models.BooleanField(null=False, db_column='sent')
    method = models.CharField(null=False, blank=False, max_length=250, db_column='method')

    log = Log('QueueMessage')

    class Meta():
        db_table = u'queue_message'
        managed = True
