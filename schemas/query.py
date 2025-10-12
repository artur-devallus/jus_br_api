from typing import List

from pydantic import BaseModel, Field


class QueryCreate(BaseModel):
    term: str = Field(min_length=11, max_length=20)


class SimpleProcess(BaseModel):
    process_number: str


class QueryOut(BaseModel):
    id: int
    query_type: str
    query_value: str
    status: str
    result_process_count: int
    processes: List[SimpleProcess]


class DetailedProcess(BaseModel):
    process_number: str
    raw_json: str


class QueryDetailedOut(BaseModel):
    id: int
    query_type: str
    query_value: str
    status: str
    result_process_count: int
    processes: List[DetailedProcess]
