from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal

PaymentType = Literal["card","upi","netbanking"]
TxStatus = Literal["pending","success","failed","refunded"]

class PaymentMethodDB(BaseModel):
    id: str
    user_id: str
    payment_type: PaymentType
    card_last_four: Optional[str] = None
    card_brand: Optional[str] = None
    upi_id: Optional[str] = None
    is_default: bool = False
    created_at: str
    updated_at: str

class PaymentMethodCreate(BaseModel):
    payment_type: PaymentType
    card_last_four: Optional[str] = None
    card_brand: Optional[str] = None
    upi_id: Optional[str] = None
    is_default: bool = False

class TransactionDB(BaseModel):
    id: str
    order_id: str
    user_id: str
    transaction_id: str
    payment_method: str
    amount: float = Field(ge=0)
    status: TxStatus
    gateway_response: Dict[str, Any] = {}
    created_at: str
    updated_at: str
