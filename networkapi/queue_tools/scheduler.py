from apscheduler.schedulers.background import BackgroundScheduler
from stompest.config import StompConfig
from stompest.sync import Stomp
from django.conf import settings
from queue_manager import QueueManager
from models import QueueMessage
import logging

LOGGER = logging.getLogger(__name__)

background_scheduler = BackgroundScheduler()


@background_scheduler.scheduled_job("interval", seconds=10)
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
        client.disconnect()
