from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any, Literal
from datetime import date

OrderStatus = Literal["pending","confirmed","packed","shipped","delivered","cancelled","refunded"]
PaymentStatus = Literal["pending","paid","failed","refunded"]
PaymentMethod = Literal["cod","online","upi"]

class OrderDB(BaseModel):
    id: str
    order_number: str
    user_id: str
    seller_id: str
    status: OrderStatus
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    subtotal: float = 0
    delivery_fee: float = 0
    tax_amount: float = 0
    discount_amount: float = 0
    total_amount: float = 0
    delivery_address: Dict[str, Any] = {}
    customer_phone: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    estimated_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    tracking_number: Optional[str] = None
    courier_partner: Optional[str] = None
    created_at: str
    updated_at: str

class OrderItemCreate(BaseModel):
    product_id: str
    product_variant_id: Optional[str] = None
    quantity: int = Field(ge=1)
    unit_price: Optional[float] = Field(default=None, ge=0)
    total_price: Optional[float] = Field(default=None, ge=0)
    # optional snapshots
    product_name: Optional[str] = None
    product_image: Optional[str] = None

class OrderCreate(BaseModel):
    seller_id: str
    payment_method: PaymentMethod = "cod"
    notes: Optional[str] = None
    delivery_address: Dict[str, Any]
    customer_phone: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    subtotal: float = Field(default=0, ge=0)
    delivery_fee: float = Field(default=0, ge=0)
    tax_amount: float = Field(default=0, ge=0)
    discount_amount: float = Field(default=0, ge=0)
    total_amount: float = Field(default=0, ge=0)
    estimated_delivery_date: Optional[date] = None

    items: List[OrderItemCreate]

    # optional tx fields
    transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None

class OrderStatusPatch(BaseModel):
    status: OrderStatus
    location: Optional[str] = None
    description: Optional[str] = None

class OrderTrackingDB(BaseModel):
    id: str
    order_id: str
    status: str
    location: Optional[str] = None
    description: Optional[str] = None
    updated_by: str
    created_at: str
