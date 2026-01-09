from pydantic import BaseModel
from typing import Optional, List, Literal

BlogStatus = Literal["draft","published","archived"]

class BlogDB(BaseModel):
    id: str
    author_id: str
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    featured_image: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    status: BlogStatus = "draft"
    view_count: int = 0
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    published_at: Optional[str] = None
    created_at: str
    updated_at: str

class BlogCreate(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    featured_image: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    status: BlogStatus = "draft"
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    published_at: Optional[str] = None

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    featured_image: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[BlogStatus] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    published_at: Optional[str] = None

class BlogStatusPatch(BaseModel):
    status: BlogStatus
