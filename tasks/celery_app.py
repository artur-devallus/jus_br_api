import os

from celery import Celery
from kombu import Queue  # noqa

from core.config import settings

celery = Celery(
    "crawler",
    broker=os.getenv("CELERY_BROKER_URL", settings.CELERY_BROKER_URL),
    backend=os.getenv("CELERY_RESULT_BACKEND", settings.CELERY_RESULT_BACKEND),
    include=[
        'tasks.crawler'
    ]
)

main_queue = 'main'
tribunal_queue = 'trf'
celery.conf.task_queues = list(map(Queue, [tribunal_queue, main_queue]))
celery.conf.task_default_queue = "main_queue"
celery.conf.task_routes = {
    "tasks.crawler.crawl_for_tribunal": dict(queue=None),
    "tasks.crawler.enqueue_crawls_for_query": dict(queue='main')
}
