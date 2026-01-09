from pydantic import BaseModel, Field
from typing import Any, Optional, List, Dict
from datetime import date

class APIResponse(BaseModel):
    message: str
    id: Optional[str] = None

class Pagination(BaseModel):
    items: List[Any] = Field(default_factory=list)
