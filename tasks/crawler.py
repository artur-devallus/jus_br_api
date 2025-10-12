import dataclasses
import traceback
from datetime import datetime
from typing import List

from celery import chord

from crud.query import upsert_process, update_query_status
from db.models import QueryStatus
from db.models.crawl_task_log import CrawlTaskLog, CrawlStatus
from db.session import SessionLocal
from lib.eproc.service import get_eproc_service
from lib.exceptions import LibJusBrException
from lib.log_utils import get_logger
from lib.models import DetailedProcessData
from lib.pje.service import get_pje_service_for_tribunal
from lib.string_utils import only_digits
from tasks.celery_app import celery, tribunal_queues
from tasks.driver_singleton import get_driver_singleton_for

log = get_logger(__name__)


@celery.task(bind=True)
def enqueue_crawls_for_query(self, query_id: int, query_type: str, query_value: str):
    log.info('Crawl for query %s with value %s', query_id, query_type)
    tribunals = tribunal_queues if query_type == 'cpf' else [
        determine_tribunal_from_process(query_value)
    ]

    tasks = [crawl_for_tribunal.s(query_id, tr, query_value).set(queue=tr) for tr in tribunals]

    chord(tasks)(finalize_query.s(query_id))


def determine_tribunal_from_process(process_number: str) -> str:
    process_number = only_digits(process_number)
    if len(process_number) != 20:
        raise RuntimeError(f"Process number {process_number} is not valid")
    process_number = int(process_number[14:16])
    if process_number < 1 or process_number > 6:
        raise RuntimeError(f"Process number {process_number} is not valid")
    return f"trf{process_number}"


@celery.task
def finalize_query(results, query_id):
    db = SessionLocal()
    update_query_status(db, query_id, QueryStatus.done)
    db.close()
    log.info(f'query of id {query_id} finished')


@celery.task(bind=True, max_retries=5, acks_late=True)
def crawl_for_tribunal(self, query_id: int, tribunal: str, term_to_search: str):
    retries = getattr(self.request, "retries", 0)
    log.info(f'Received task with query id {query_id} tribunal {tribunal} and term_to_search {term_to_search}')

    db = SessionLocal()
    crawl_task_log = CrawlTaskLog(
        tribunal=tribunal,
        status=CrawlStatus.running,
        query_id=query_id,
        attempts=0
    )
    if retries >= self.max_retries:
        if all_crawls_finished(db, query_id):
            update_query_status(db, query_id, QueryStatus.done)
        return

    db.add(crawl_task_log)
    db.commit()
    db.refresh(crawl_task_log)
    try:
        driver = get_driver_singleton_for(tribunal)
        results = run_crawler(driver, tribunal, term_to_search)
        count = 0
        process = None
        for r in results:
            process = upsert_process(
                db,
                query_id=query_id,
                crawl_task_log_id=crawl_task_log.id,
                tribunal=tribunal,
                process_number=only_digits(r.process.process_number),
                raw_json=dataclasses.asdict(r)
            )
        count += len(results)

        update_query_status(db, query_id, QueryStatus.running, count)
        crawl_task_log.status = CrawlStatus.done
        crawl_task_log.process_id = process.id if process else None
        crawl_task_log.finished_at = datetime.now()
        db.add(crawl_task_log)
        db.commit()
        if all_crawls_finished(db, query_id):
            update_query_status(db, query_id, QueryStatus.done)
        log.info(
            f'Crawl for {query_id} tribunal {tribunal} and term_to_search {term_to_search} completed successfully'
        )
    except Exception as exc:
        log.error('Crawl task failed', exc_info=exc)
        crawl_task_log.status = CrawlStatus.failed
        crawl_task_log.attempts = (crawl_task_log.attempts or 0) + 1
        crawl_task_log.last_error = traceback.format_exc()
        db.add(crawl_task_log)
        db.commit()
        raise self.retry(exc=exc, countdown=10 * (self.request.retries + 1))
    finally:
        db.close()


def all_crawls_finished(db, query_id):
    total = db.query(CrawlTaskLog).filter_by(query_id=query_id).count()
    finished = db.query(CrawlTaskLog).filter(
        CrawlTaskLog.query_id == query_id,
        CrawlTaskLog.status.in_(["done", "failed"])
    ).count()
    return total > 0 and total == finished


def _get_for_grade(term, grade, tribunal, driver):
    all_processes = []
    try:
        pje_service = get_pje_service_for_tribunal(tribunal=tribunal, driver=driver)
        process_list = pje_service.get_process_list(
            term=term, grade=grade
        )

        for process in process_list:
            try:
                all_processes.append(pje_service.get_detailed_process(
                    term=term, grade=grade, process_index_or_number=process.process_number,
                ))
            except LibJusBrException as ex:
                log.warning(ex.message)

    except LibJusBrException as ex:
        log.warning(ex.message)

    return all_processes


def _get_for_eproc(term, grade, tribunal, driver):
    all_processes = []
    try:
        eproc_service = get_eproc_service(tribunal=tribunal, driver=driver)
        process_list = eproc_service.get_process_list(
            term=term, grade=grade
        )
        for process in process_list:
            try:
                all_processes.append(eproc_service.get_detailed_process(
                    term=term, grade=grade, process_index_or_number=process.process_number,
                ))
            except LibJusBrException as ex:
                log.warning(ex.message)
    except LibJusBrException as ex:
        log.warning(ex.message)

    return all_processes


def run_crawler(driver, tribunal, term) -> List[DetailedProcessData]:
    all_processes = []
    for grade in ['pje1g', 'pje2g']:
        all_processes.extend(_get_for_grade(term, grade, tribunal, driver))

    all_processes.extend(_get_for_eproc(term, grade, tribunal, driver))

    return all_processes
