import gzip

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_current_user
from crud.query import create_query, get_query_by_term
from db.models.query import Query as QueryModel, Query
from db.session import get_db
from schemas.query import QueryCreate, QueryOut, SimpleProcess, QueryDetailedOut, DetailedProcess
from tasks.crawler import enqueue_crawls_for_query

router = APIRouter(prefix="/queries", tags=["queries"])


@router.post("/", response_model=QueryOut)
def create_query_endpoint(payload: QueryCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    existing = get_query_by_term(db, str(payload.term))
    if existing:
        q = existing
    else:
        q = create_query(db, user.id, payload.term)
        enqueue_crawls_for_query.delay(q.id, q.query_type, q.query_value)
    return QueryOut(
        id=q.id,
        query_type=q.query_type,
        query_value=q.query_value,
        status=q.status,
        result_process_count=q.result_process_count,
        processes=[]
    )


@router.get("/{query_id}", response_model=QueryOut)
def get_query(query_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    q: Query = db.query(QueryModel).get(query_id)
    if not q:
        raise HTTPException(404, "Not found")
    if q.user_id != user.id and "admin" not in [g.name for g in user.groups]:
        raise HTTPException(403, "Forbidden")
    return QueryOut(
        id=q.id,
        query_type=q.query_type,
        query_value=q.query_value,
        status=q.status,
        result_process_count=q.result_process_count,
        processes=[SimpleProcess(
            process_number=p.process_number,
        ) for p in q.process]
    )


@router.get("/{query_id}/detailed", response_model=QueryDetailedOut)
def get_query_detailed(query_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(QueryModel).get(query_id)
    if not q:
        raise HTTPException(404, "Not found")
    if q.user_id != user.id and "admin" not in [g.name for g in user.groups]:
        raise HTTPException(403, "Forbidden")
    return QueryDetailedOut(
        id=q.id,
        query_type=q.query_type,
        query_value=q.query_value,
        status=q.status,
        result_process_count=q.result_process_count,
        processes=[DetailedProcess(
            process_number=p.process_number,
            raw_json=gzip.decompress(p.raw_json).decode("utf-8"),
        ) for p in q.process]
    )
