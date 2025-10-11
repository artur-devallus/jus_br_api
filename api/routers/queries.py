from tasks.crawler import enqueue_crawls_for_query
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_current_user
from crud.query import create_query
from db.session import get_db
from db.models.query import Query as QueryModel
from schemas.query import QueryCreate, QueryOut

router = APIRouter(prefix="/queries", tags=["queries"])


@router.post("/", response_model=QueryOut)
def create_query_endpoint(payload: QueryCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: check credits atomic debit (omitted brevity)
    q = create_query(db, user.id, payload.query_type, payload.query_value)
    # enqueue tasks
    enqueue_crawls_for_query.delay(q.id, payload.query_type, payload.query_value)
    return {"id": q.id, "query_type": q.query_type, "query_value": q.query_value, "status": q.status.value,
            "result_process_count": q.result_process_count}


@router.get("/{query_id}", response_model=QueryOut)
def get_query(query_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(QueryModel).get(query_id)
    if not q:
        raise HTTPException(404, "Not found")
    if q.user_id != user.id and "admin" not in [g.name for g in user.groups]:
        raise HTTPException(403, "Forbidden")
    return {"id": q.id, "query_type": q.query_type, "query_value": q.query_value, "status": q.status.value,
            "result_process_count": q.result_process_count}


@router.get("/{query_id}/detailed")
def get_query_detailed(query_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(QueryModel).get(query_id)
    if not q:
        raise HTTPException(404, "Not found")
    if q.user_id != user.id and "admin" not in [g.name for g in user.groups]:
        raise HTTPException(403, "Forbidden")
    # return processes + movements simplified
    return {
        "id": q.id,
        "processes": [
            {
                "tribunal": p.tribunal,
                "process_number": p.process_number,
                "raw_json": p.raw_json
            } for p in q.processes
        ]
    }
