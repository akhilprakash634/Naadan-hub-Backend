from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ProductDB(BaseModel):
    id: str
    seller_id: str
    name: str
    slug: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    price: float = 0
    original_price: Optional[float] = None
    discount_percentage: Optional[int] = None
    unit: Optional[str] = None
    stock_quantity: int = 0
    min_order_quantity: int = 1
    max_order_quantity: Optional[int] = None
    sku: str
    images: List[str] = []
    nutritional_info: Dict[str, Any] = {}
    storage_instructions: Optional[str] = None
    shelf_life: Optional[str] = None
    origin: Optional[str] = None
    is_organic: bool = False
    is_featured: bool = False
    is_active: bool = True
    total_sold: int = 0
    rating: float = 0
    review_count: int = 0
    tags: List[str] = []
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    created_at: str
    updated_at: str

class ProductCreate(BaseModel):
    # seller_id normally derived from token; keep optional for admin
    seller_id: Optional[str] = None
    name: str
    slug: str
    sku: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    price: float = Field(ge=0)
    original_price: Optional[float] = Field(default=None, ge=0)
    discount_percentage: Optional[int] = Field(default=None, ge=0, le=100)
    unit: Optional[str] = None
    stock_quantity: int = Field(default=0, ge=0)
    min_order_quantity: int = Field(default=1, ge=1)
    max_order_quantity: Optional[int] = Field(default=None, ge=1)
    images: List[str] = []
    nutritional_info: Dict[str, Any] = {}
    storage_instructions: Optional[str] = None
    shelf_life: Optional[str] = None
    origin: Optional[str] = None
    is_organic: bool = False
    is_featured: bool = False
    is_active: bool = True
    tags: List[str] = []
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    original_price: Optional[float] = Field(default=None, ge=0)
    discount_percentage: Optional[int] = Field(default=None, ge=0, le=100)
    unit: Optional[str] = None
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    min_order_quantity: Optional[int] = Field(default=None, ge=1)
    max_order_quantity: Optional[int] = Field(default=None, ge=1)
    images: Optional[List[str]] = None
    nutritional_info: Optional[Dict[str, Any]] = None
    storage_instructions: Optional[str] = None
    shelf_life: Optional[str] = None
    origin: Optional[str] = None
    is_organic: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None

class ProductStatusPatch(BaseModel):
    is_active: bool

class ProductVariantDB(BaseModel):
    id: str
    product_id: str
    variant_name: str
    price: float = 0
    stock_quantity: int = 0
    sku: str
    is_active: bool = True
    created_at: str
    updated_at: str

class ProductVariantCreate(BaseModel):
    product_id: str
    variant_name: str
    price: float = Field(ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    sku: str
    is_active: bool = True

class ProductVariantUpdate(BaseModel):
    variant_name: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    sku: Optional[str] = None
    is_active: Optional[bool] = None
