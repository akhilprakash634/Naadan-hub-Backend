from pydantic import BaseModel
from typing import Optional, List

class BSFEducationDB(BaseModel):
    id: str
    section: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    images: List[str] = []
    video_url: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    created_at: str
    updated_at: str

class BSFEducationUpsert(BaseModel):
    id: Optional[str] = None
    section: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    images: List[str] = []
    video_url: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
