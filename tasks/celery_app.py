from celery import Celery
from kombu import Queue  # noqa

from core.config import settings

celery = Celery(
    "crawler",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'tasks.crawler'
    ]
)

main_queue = 'main'
tribunal_queues = ['trf1', 'trf2', 'trf3', 'trf4', 'trf5', 'trf6']

celery.conf.task_queues = list(map(Queue, tribunal_queues + [main_queue]))
celery.conf.task_default_queue = "main_queue"
celery.conf.task_routes = {
    "tasks.crawler.crawl_for_tribunal": dict(queue=None),
    "tasks.crawler.enqueue_crawls_for_query": dict(queue='main')
}
