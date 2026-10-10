from typing import Literal

from pydantic import BaseModel

Status = Literal["PASS", "FAIL"]


class ErrorResponse(BaseModel):
    detail: str