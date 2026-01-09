from pydantic import BaseModel
from typing import Optional, Literal

ApprovalStatus = Literal["pending", "approved", "rejected"]

class SellerProfileDB(BaseModel):
    id: str
    user_id: str
    farm_name: str
    farm_description: Optional[str] = None
    farm_location: Optional[str] = None
    farm_address: Optional[str] = None
    farm_size: Optional[str] = None
    certification_type: Optional[str] = None
    certification_number: Optional[str] = None
    certification_document_url: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    approval_status: ApprovalStatus = "pending"
    rejection_reason: Optional[str] = None
    rating: float = 0
    total_sales: float = 0
    total_orders: int = 0
    is_verified: bool = False
    created_at: str
    updated_at: str

class SellerProfileUpdateRequest(BaseModel):
    farm_name: Optional[str] = None
    farm_description: Optional[str] = None
    farm_location: Optional[str] = None
    farm_address: Optional[str] = None
    farm_size: Optional[str] = None
    certification_type: Optional[str] = None
    certification_number: Optional[str] = None
    certification_document_url: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None

    # admin-only fields (enforce in router)
    approval_status: Optional[ApprovalStatus] = None
    rejection_reason: Optional[str] = None
    is_verified: Optional[bool] = None
