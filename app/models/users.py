from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, Literal
from datetime import date

UserRole = Literal["user", "seller", "admin"]
UserStatus = Literal["active", "inactive", "suspended"]
Gender = Literal["male", "female", "other"]

class UserDB(BaseModel):
    id: str
    email: EmailStr
    password_hash: Optional[str] = None
    full_name: str
    phone: Optional[str] = None
    role: UserRole = "user"
    google_id: Optional[str] = None
    email_verified: bool = False
    status: UserStatus = "active"
    created_at: str
    updated_at: str

class UserProfileDB(BaseModel):
    id: str
    user_id: str
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    bio: Optional[str] = None
    preferences: Dict[str, Any] = {}
    created_at: str
    updated_at: str

class ProfileUpdateRequest(BaseModel):
    # user fields
    full_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[UserStatus] = None  # admin can set; you can enforce in router

    # profile fields
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class ProfileResponse(BaseModel):
    user: UserDB
    profile: Optional[UserProfileDB] = None
