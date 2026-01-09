from pydantic import BaseModel, Field
from typing import Optional, Literal

AddressType = Literal["home", "work", "other"]

class DeliveryAddressDB(BaseModel):
    id: str
    user_id: str
    address_type: AddressType = "home"
    full_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    pincode: str = Field(min_length=4, max_length=10)
    landmark: Optional[str] = None
    is_default: bool = False
    created_at: str
    updated_at: str

class AddressUpsertRequest(BaseModel):
    id: Optional[str] = None
    address_type: AddressType = "home"
    full_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    pincode: str = Field(min_length=4, max_length=10)
    landmark: Optional[str] = None
    is_default: bool = False
