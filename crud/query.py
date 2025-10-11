from datetime import datetime

from db.models.process import Process
from db.models.query import Query, QueryStatus
from sqlalchemy.orm import Session


def create_query(db: Session, user_id: int, query_type: str, query_value: str):
    q = Query(user_id=user_id, query_type=query_type, query_value=query_value, status=QueryStatus.queued)
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def update_query_status(db: Session, query_id: int, status: QueryStatus, result_count: int | None = None):
    q = db.query(Query).get(query_id)
    if not q:
        return None
    q.status = status
    if result_count is not None:
        q.result_process_count = result_count
    q.meta = q.meta or {}
    q.meta["last_status_changed_at"] = datetime.now().isoformat()
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def upsert_process(db: Session, tribunal: str, process_number: str, raw_json: dict):
    p = db.query(Process).filter(
        Process.tribunal == tribunal,
        Process.process_number == process_number
    ).first()
    if p:
        p.raw_json = raw_json
        p.last_crawl_at = datetime.now()
    else:
        p = Process(tribunal=tribunal, process_number=process_number, raw_json=raw_json,
                    last_crawl_at=datetime.now())
        db.add(p)
    db.commit()
    db.refresh(p)
    return p
