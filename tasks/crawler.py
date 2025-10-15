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
from lib.trf5.service import get_trf5_service
from tasks.celery_app import celery, tribunal_queue
from tasks.driver_singleton import get_driver_singleton

log = get_logger(__name__)
all_tribunals = ['trf1', 'trf2', 'trf3', 'trf4', 'trf5', 'trf6']


@celery.task(bind=True)
def enqueue_crawls_for_query(self, query_id: int, query_type: str, query_value: str):
    log.info('Crawl for query %s with value %s', query_id, query_type)
    tribunals = all_tribunals if query_type == 'cpf' else [
        determine_tribunal_from_process(query_value)
    ]
    tasks = []
    db = SessionLocal()
    try:
        for tribunal in tribunals:
            crawl_task_log = CrawlTaskLog(
                tribunal=tribunal,
                status=CrawlStatus.running,
                query_id=query_id,
                attempts=0
            )
            db.add(crawl_task_log)
            db.commit()
            db.refresh(crawl_task_log)
            tasks.append(crawl_for_tribunal.s(query_id, crawl_task_log.id, query_value).set(queue=tribunal_queue))
        chord(tasks)(finalize_query.s(query_id))
    finally:
        db.close()


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
def crawl_for_tribunal(self, query_id: int, crawl_task_log_id: int, term_to_search: str):
    retries = getattr(self.request, "retries", 0)
    log.info(f'Received task: query_id={query_id} crawl_task_log={crawl_task_log_id} term_to_search={term_to_search}')

    db = SessionLocal()
    if retries >= self.max_retries:
        if all_crawls_finished(db, query_id):
            update_query_status(db, query_id, QueryStatus.done)
        return

    crawl_task_log: CrawlTaskLog = db.query(CrawlTaskLog).get(CrawlTaskLog.id)

    try:
        driver = get_driver_singleton()
        results = run_crawler(driver, crawl_task_log.tribunal, term_to_search)
        count = 0
        process = None
        for r in results:
            process = upsert_process(
                db,
                query_id=query_id,
                crawl_task_log_id=crawl_task_log.id,
                tribunal=crawl_task_log.tribunal,
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
            f'Task finished: query_id={query_id} crawl_task_log={crawl_task_log_id} term_to_search={term_to_search}'
        )
    except Exception as exc:
        log.error(
            f'Task failed: query_id={query_id} crawl_task_log={crawl_task_log_id} term_to_search={term_to_search}',
            exc_info=exc
        )
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
        log.info(f'running for {tribunal} {grade}')
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
        log.info(f'running for {tribunal} {grade}')
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


def _get_for_trf5(term, driver):
    all_processes = []

    try:
        log.info(f'running for trf5')
        service = get_trf5_service(driver)
        process_list = service.get_process_list(
            term=term
        )
        for process in process_list:
            try:
                all_processes.append(service.get_detailed_process(
                    term=term, process_index_or_number=process.process_number,
                ))
            except LibJusBrException as ex:
                log.warning(ex.message)
    except LibJusBrException as ex:
        log.warning(ex.message)

    return all_processes


def run_crawler(driver, tribunal, term) -> List[DetailedProcessData]:
    all_processes = []
    if tribunal in ['trf1', 'trf3', 'trf6']:
        for grade in ['pje1g', 'pje2g']:
            all_processes.extend(_get_for_grade(term, grade, tribunal, driver))

    if tribunal == 'trf2':
        all_processes.extend(_get_for_eproc(term, 'eproc1g', tribunal, driver))

    if tribunal == 'trf5':
        all_processes.extend(_get_for_trf5(term, driver))

    if tribunal == 'trf6':
        for grade in ['eproc1g', 'eproc2g']:
            all_processes.extend(_get_for_grade(term, grade, tribunal, driver))

    return all_processes
