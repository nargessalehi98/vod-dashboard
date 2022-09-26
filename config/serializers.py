from typing import Optional

from pydantic import BaseModel, validator


class InputSerializer(BaseModel):
    method: str
    auth: Optional[str]
    api_version: Optional[str]
    data: dict


class PaginationSerializer(BaseModel):
    skip: Optional[int] = 0
    limit: Optional[int] = 10

    @validator('limit')
    def limit_is_valid(cls, limit):
        if limit > 100:
            raise ValueError('limit is not valid')
        return limit
