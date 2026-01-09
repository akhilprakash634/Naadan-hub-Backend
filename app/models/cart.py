from pydantic import BaseModel, Field
from typing import Optional

class CartItemDB(BaseModel):
    id: str
    user_id: str
    product_id: str
    product_variant_id: Optional[str] = None
    quantity: int = Field(ge=1)
    created_at: str
    updated_at: str

class CartItemCreate(BaseModel):
    product_id: str
    product_variant_id: Optional[str] = None
    quantity: int = Field(default=1, ge=1)

class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)
