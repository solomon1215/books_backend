
import logging
import os
import time
from threading import Thread
from subprocess import Popen, PIPE
from config.settings import settings


_logger = logging.getLogger(__name__)


class CeleryJob(object):

    def __init__(self, app):
        self.restart = True
        self.app = app

    def poll(self):
        return None

    def start_celery(self, path):
        if self.restart:
            p = Popen(["celery", "worker", "-A", "workers", "--loglevel=info"], cwd=path, stdin=PIPE)  # env pass the broker and queue
            return p
        else:
            return self

    def check_status(self):
        path = os.path.abspath(os.path.dirname(__name__))
        c = self.start_celery(path)
        while 1:
            if c.poll() is not None:
                c = self.start_celery(path)
            time.sleep(10)

    def run(self):
        thr = Thread(name='celery_thread', target=self.check_status)
        thr.daemon = True
        thr.start()

    def stop(self):
        self.restart = False


def celery_start(app):
    _logger.info("Celery starting...")
    celery_thread = CeleryJob(app)
    celery_thread.run()
    app.celery = celery_thread


async def celery_stop(app, loop):
    _logger.info("Celery stopping...")
    app.celery.stop()


