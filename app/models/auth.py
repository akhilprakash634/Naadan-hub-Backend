from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=2)
    phone: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SellerRegisterRequest(RegisterRequest):
    farm_name: str = Field(min_length=2)
    farm_description: Optional[str] = None
    farm_location: Optional[str] = None
    farm_address: Optional[str] = None
    farm_size: Optional[str] = None

class GoogleAuthRequest(BaseModel):
    idToken: str

class MeResponse(BaseModel):
    uid: str
    email: Optional[EmailStr] = None
    role: str
    status: str
