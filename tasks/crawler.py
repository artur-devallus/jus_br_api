import dataclasses
import traceback
from datetime import datetime
from typing import List

from crud.query import upsert_process, update_query_status
from db.models import QueryStatus
from db.models.crawl_task_log import CrawlTaskLog
from db.session import SessionLocal
from lib.eproc.service import get_eproc_service
from lib.exceptions import LibJusBrException
from lib.models import DetailedProcessData
from lib.pje.service import get_pje_service_for_tribunal
from lib.string_utils import only_digits
from tasks.celery_app import celery
from tasks.driver_singleton import get_driver_singleton_for


@celery.task(bind=True, max_retries=5, acks_late=True)
def crawl_for_tribunal(self, query_id: int, tribunal: str, term_to_search: str):
    db = SessionLocal()
    log = CrawlTaskLog(tribunal=tribunal, status='started', attempts=0)
    db.add(log)
    db.commit()
    db.refresh(log)
    try:
        driver = get_driver_singleton_for(tribunal)
        results = run_crawler(driver, tribunal, term_to_search)
        count = 0
        for r in results:
            upsert_process(
                db,
                tribunal=tribunal,
                process_number=only_digits(r.process.process_number),
                raw_json=dataclasses.asdict(r)
            )
        count += len(results)

        update_query_status(db, query_id, QueryStatus.running, count)  # partial
        log.status = 'done'
        log.finished_at = datetime.now()
        db.add(log)
        db.commit()
    except Exception as exc:
        log.status = 'failed'
        log.attempts = (log.attempts or 0) + 1
        log.last_error = traceback.format_exc()
        db.add(log)
        db.commit()
        raise self.retry(exc=exc, countdown=10 * (self.request.retries + 1))
    finally:
        db.close()


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
            except LibJusBrException:
                ...

    except LibJusBrException:
        ...

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
            except LibJusBrException:
                ...
    except LibJusBrException:
        ...

    return all_processes


def run_crawler(driver, tribunal, term) -> List[DetailedProcessData]:
    all_processes = []
    for grade in ['pje1g', 'pje2g']:
        all_processes.extend(_get_for_grade(term, grade, tribunal, driver))

    all_processes.extend(_get_for_eproc(term, grade, tribunal, driver))

    return all_processes
