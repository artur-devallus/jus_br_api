from celery import Celery

from core.config import settings
from lib.string_utils import only_digits
from tasks.crawler import crawl_for_tribunal

celery = Celery(
    "crawler",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)
from kombu import Queue

celery.conf.task_queues = [
    Queue("trf1"),
    Queue("trf2"),
    Queue("trf3"),
    Queue("trf4"),
    Queue("trf5"),
    Queue("trf6")
]
celery.conf.task_default_queue = "trf1"
celery.conf.task_routes = {
    "app.tasks.crawler.crawl_for_tribunal": {"queue": "trf1"}  # default route only
}


# helper to enqueue one task per tribunal or single for process
@celery.task(bind=True)
def enqueue_crawls_for_query(self, query_id: int, query_type: str, query_value: str):
    # dispatch one task per tribunal for cpf
    tribunals = ["trf1", "trf2", "trf3", "trf4", "trf5", "trf6"] if query_type == "cpf" else [
        determine_tribunal_from_process(query_value)
    ]
    for tr in tribunals:
        crawl_for_tribunal.apply_async(args=[query_id, tr, query_value], queue=tr)


def determine_tribunal_from_process(process_number: str) -> str:
    process_number =only_digits(process_number)
    # simple detection by pattern; adapt as needed
    # fallback to trf1
    return "trf1"
