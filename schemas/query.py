from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class QueryCreate(BaseModel):
    term: str = Field(min_length=11, max_length=25)
    enqueue: bool = Field(default=False)


class SimpleProcess(BaseModel):
    process_number: str


class QueryOut(BaseModel):
    id: int
    query_type: str
    query_value: str
    status: str
    result_process_count: int
    processes: List[SimpleProcess] = []

    model_config = ConfigDict(from_attributes=True)


class DetailedProcess(BaseModel):
    process_number: str
    raw_json: Optional[str] = None


class QueryDetailedOut(BaseModel):
    id: int
    query_type: str
    query_value: str
    status: str
    result_process_count: int
    processes: List[DetailedProcess]

    model_config = ConfigDict(from_attributes=True)
