from pydantic import BaseModel, Field


class Response(BaseModel):
    status_code: int
    body: dict
    headers: dict
