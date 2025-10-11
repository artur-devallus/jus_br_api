from typing import Literal

from pydantic import BaseModel, Field


class QueryCreate(BaseModel):
    query_type: Literal["cpf", "processo"]
    query_value: str = Field(max_length=20, min_length=20)


class QueryOut(BaseModel):
    id: int
    query_type: str
    query_value: str
    status: str
    result_process_count: int
