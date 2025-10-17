import gzip
import json
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam
from sqlalchemy.orm import Session, load_only

from api.deps import get_current_user
from crud.query import create_query, get_query_by_term, update_query_status
from db.models import Process, CrawlTaskLog
from db.models.query import Query as QueryModel, QueryStatus
from db.session import get_db
from schemas.query import (
    QueryCreate,
    QueryOut,
    SimpleProcess,
    QueryDetailedOut,
    DetailedProcess, QueryEnqueue,
)
from tasks.crawler import enqueue_crawls_for_query

router = APIRouter(prefix="/queries", tags=["Queries"])


def _authorize_query(query: QueryModel, user):
    if query.user_id != user.id and "admin" not in [g.name for g in user.groups]:
        raise HTTPException(403, "Forbidden")


def _decompress_raw_json(raw_json: bytes | None) -> str | None:
    if not raw_json:
        return None
    try:
        return gzip.decompress(raw_json).decode("utf-8")
    except (RuntimeError, Exception):
        return None


def _remove_keys(json_str: str, keys_to_remove) -> str:
    data = json.loads(json_str)
    for key in keys_to_remove:
        if key in data:
            del data[key]
    return json.dumps(data)


@router.get("", response_model=list[QueryOut])
def list_queries(
        user=Depends(get_current_user),
        db: Session = Depends(get_db),
        query_value: str = QueryParam(None, max_length=20, min_length=11),
        result_process_count_ge: int = QueryParam(None, ge=0),
        tribunal: str = QueryParam(None, max_length=4, min_length=4),
        page: int = QueryParam(1, ge=1),
        size: int = QueryParam(20, ge=1, le=1000),
):
    query = db.query(QueryModel).order_by(QueryModel.created_at.desc())

    if 'admin' not in [g.name for g in user.groups]:
        query = query.filter(QueryModel.user_id == user.id)

    if query_value is not None:
        query = query.filter(QueryModel.query_value == query_value)

    if tribunal is not None:
        queries = db.query(
            Process
        ).filter(
            Process.tribunal == tribunal
        ).options(load_only(
            Process.query_id
        )).all()
        query = query.filter(QueryModel.id.in_([x.query_id for x in queries]))
    elif result_process_count_ge is not None:
        query = query.filter(QueryModel.result_process_count >= result_process_count_ge)

    results: List[Any] = query.order_by(QueryModel.id.desc()).offset((page - 1) * size).limit(size).all()

    return [
        QueryOut(
            id=q.id,
            query_type=q.query_type,
            query_value=q.query_value,
            created_at=q.created_at,
            status=q.status,
            result_process_count=(
                q.result_process_count if tribunal is None else db.query(Process).filter(
                    Process.query_id == q.id, Process.tribunal == tribunal
                ).count()
            ),
        ) for q in results
    ]


@router.post("", response_model=QueryDetailedOut)
def create_query_endpoint(
        payload: QueryCreate, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    existing = get_query_by_term(db, str(payload.term))

    if existing:
        q = existing
        if q.status != QueryStatus.done and payload.enqueue:
            enqueue_crawls_for_query.delay(q.id, q.query_type, q.query_value, False)
            update_query_status(db, q.id, QueryStatus.queued)
    else:
        q = create_query(db, user.id, payload.term)
        if payload.enqueue:
            enqueue_crawls_for_query.delay(q.id, q.query_type, q.query_value, False)

    return QueryDetailedOut(
        id=q.id,
        query_type=q.query_type,
        query_value=q.query_value,
        created_at=q.created_at,
        status=q.status,
        result_process_count=q.result_process_count,
        processes=[
            DetailedProcess(
                process_number=p.process_number,
                raw_json=_remove_keys(_decompress_raw_json(p.raw_json), ['attachments']),
            )
            for p in q.process
        ],
    )


@router.get("/{query_id}", response_model=QueryOut)
def get_query(query_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(QueryModel).get(query_id)
    if not q:
        raise HTTPException(404, "Not found")

    _authorize_query(q, user)

    return QueryOut(
        id=q.id,
        query_type=q.query_type,
        query_value=q.query_value,
        created_at=q.created_at,
        status=q.status,
        result_process_count=q.result_process_count,
        processes=[SimpleProcess(process_number=p.process_number) for p in q.process],
    )


@router.get("/{query_id}/detailed", response_model=QueryDetailedOut)
def get_query_detailed(query_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(QueryModel).get(query_id)
    if not q:
        raise HTTPException(404, "Not found")

    _authorize_query(q, user)

    return QueryDetailedOut(
        id=q.id,
        query_type=q.query_type,
        query_value=q.query_value,
        created_at=q.created_at,
        status=q.status,
        result_process_count=q.result_process_count,
        processes=[
            DetailedProcess(
                process_number=p.process_number,
                raw_json=_remove_keys(_decompress_raw_json(p.raw_json), ['attachments']),
            )
            for p in q.process
        ],
    )


@router.post("/{query_id}/enqueue", response_model=QueryOut)
def enqueue_query(
        query_id: int,
        payload: QueryEnqueue,
        user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    q = db.query(QueryModel).get(query_id)
    if not q:
        raise HTTPException(404, "Not found")

    _authorize_query(q, user)

    update_query_status(db, q.id, QueryStatus.queued)
    enqueue_crawls_for_query.delay(q.id, q.query_type, q.query_value, payload.force)

    return QueryOut.model_validate(q)
