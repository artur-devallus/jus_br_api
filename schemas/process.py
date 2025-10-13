import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from db.models.process import Tribunal


class MovementSchema(BaseModel):
    created_at: datetime.datetime
    description: str
    document_ref: Optional[str] = None
    document_date: Optional[datetime.datetime] = None


class ProcessSummarySchema(BaseModel):
    tribunal: str
    process_number: str
    distribution_date: Optional[datetime.date] = None


class ProcessDetailedSchema(ProcessSummarySchema):
    raw_json: Optional[dict]
    movements: List[MovementSchema] = []


class ProcessOut(BaseModel):
    id: int
    query_id: Optional[int]
    tribunal: Optional[Tribunal]
    process_number: str
    last_crawl_at: Optional[datetime.datetime]
    distribution_date: Optional[datetime.date]

    model_config = ConfigDict(from_attributes=True)


class ProcessDetail(BaseModel):
    id: int
    tribunal: Optional[Tribunal]
    process_number: str
    distribution_date: Optional[datetime.date]
    last_crawl_at: Optional[datetime.datetime]
    raw_json: Optional[str]

    model_config = ConfigDict(from_attributes=True)
