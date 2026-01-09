from pydantic import BaseModel, Field
from typing import Optional, List

class ReviewDB(BaseModel):
    id: str
    user_id: str
    product_id: Optional[str] = None
    seller_id: Optional[str] = None
    order_id: str
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None
    images: List[str] = []
    is_verified_purchase: bool = False
    helpful_count: int = Field(default=0, ge=0)
    created_at: str
    updated_at: str

class ReviewCreate(BaseModel):
    product_id: Optional[str] = None
    seller_id: Optional[str] = None
    order_id: str
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None
    images: List[str] = []
