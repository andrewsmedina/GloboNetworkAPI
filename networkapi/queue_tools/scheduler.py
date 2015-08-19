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


from apscheduler.schedulers.background import BackgroundScheduler
from stompest.config import StompConfig
from stompest.sync import Stomp
from django.conf import settings
from queue_manager import QueueManager
from models import QueueMessage
import logging
from django.db import connection

LOGGER = logging.getLogger(__name__)

background_scheduler = BackgroundScheduler()


@background_scheduler.scheduled_job("interval", seconds=settings.SCHEDULER_INTERVAL)
def resend_failed_messages():

    """
        Create a job to resend all messages that
        haven't been sent successfully
    """

    queue_manager = QueueManager()

    configuration = StompConfig(uri=settings.QUEUE_BROKER_URI)
    client = Stomp(configuration)

    try:
        client.connect(connectTimeout=settings.QUEUE_BROKER_CONNECT_TIMEOUT)
        messages = QueueMessage.objects.filter(sent=False)

        LOGGER.debug('{} messages found'.format(len(messages)))

        for message in messages:
            queue_manager.resend(message, client)

    except Exception, e:
        print e

    finally:
        connection.close()

        if client.session._state == client.session.CONNECTED:
            client.disconnect()
