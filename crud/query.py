import gzip
import json
from datetime import datetime

from sqlalchemy.orm import Session

from db.models.process import Process
from db.models.query import Query, QueryStatus
from lib.json_utils import default_json_encoder


def create_query(db: Session, user_id: int, term: str):
    q = Query(
        user_id=user_id,
        query_type='cpf' if len(term) == 11 else 'process',
        query_value=term,
        status=QueryStatus.queued
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def get_query_by_term(db: Session, term: str):
    return db.query(Query).filter(
        Query.query_value == term
    ).first()


def update_query_status(db: Session, query_id: int, status: QueryStatus, result_count: int | None = None):
    q = db.query(Query).get(query_id)
    if not q:
        return None
    q.status = status
    if result_count is not None:
        q.result_process_count = int(q.result_process_count or 0) + result_count
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def upsert_process(
        db: Session, query_id: int, crawl_task_log_id: int, tribunal: str, process_number: str, raw_json: dict
):
    p = db.query(Process).filter(
        Process.tribunal == tribunal,
        Process.process_number == process_number
    ).first()
    gziped = gzip.compress(json.dumps(raw_json, default=default_json_encoder).encode('utf-8'))
    if p:
        p.raw_json = gziped
        p.last_crawl_at = datetime.now()
    else:
        p = Process(
            query_id=query_id,
            crawl_task_log_id=crawl_task_log_id,
            tribunal=tribunal,
            process_number=process_number,
            raw_json=gziped,
            last_crawl_at=datetime.now()
        )
        db.add(p)
    db.commit()
    db.refresh(p)
    return p
