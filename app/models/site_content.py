from pydantic import BaseModel
from typing import Dict, Any, Optional

class SiteContentDB(BaseModel):
    id: str
    section: str
    content: Dict[str, Any]
    created_at: str
    updated_at: str

class SiteContentUpdate(BaseModel):
    content: Dict[str, Any]
