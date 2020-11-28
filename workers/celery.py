from __future__ import absolute_import, unicode_literals
from celery import Celery

from config.settings import settings

broker = settings.get('MQ_BROKER')
backend = 'redis://default:%s@%s:%s/%s' % (settings.get('REDIS_PASS'), settings.get('REDIS_HOST'), settings.get('REDIS_PORT'), settings.get('REDIS_DB'))

# broker='amqp://admin:1qaz2wsX3edc@localhost//'
# backend = 'redis://default:1qaz2wsX3edc@localhost:6379/9'

app = Celery('Workers', broker=broker, backend=backend, include=['workers.tasks'])

app.conf.update(
    result_expires=3600,
    # task_serializer='json',
    # accept_content=['json'],
    # result_serializer='json',
    enable_utc=True,
)

if __name__ == '__main__':
    app.start()