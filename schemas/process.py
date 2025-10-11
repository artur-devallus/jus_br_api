import datetime
from typing import Optional, List

from pydantic import BaseModel


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
