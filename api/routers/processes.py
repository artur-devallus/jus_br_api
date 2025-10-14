from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from db.models.process import Process, Tribunal
from db.session import get_db
from schemas.process import ProcessOut, ProcessDetail

router = APIRouter(prefix="/processes", tags=["Processes"])


@router.get('', response_model=List[ProcessOut])
def list_processes(
        db: Session = Depends(get_db),
        tribunal: Optional[Tribunal] = Query(None),
        process_number: Optional[str] = Query(None),
        query_id: Optional[int] = Query(None),
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
):
    query = db.query(Process)

    if tribunal:
        query = query.filter(Process.tribunal == tribunal)
    if process_number:
        query = query.filter(Process.process_number.like(f"%{process_number}%"))
    if query_id:
        query = query.filter(Process.query_id == query_id)
    if start_date:
        query = query.filter(Process.distribution_date >= start_date)
    if end_date:
        query = query.filter(Process.distribution_date <= end_date)

    processes = (
        query.order_by(Process.last_crawl_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return [ProcessOut.model_validate(p) for p in processes]


@router.get("/{process_id}", response_model=ProcessDetail)
def get_process_detail(process_id: int, db: Session = Depends(get_db)):
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    return ProcessDetail.model_validate(process)
