from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    city: str
    state: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    age: int
    profession: str
    language: str = "English"
    password: str
    role: str = "user"


class UserLogin(BaseModel):
    identifier: str
    password: str


class PasswordReset(BaseModel):
    identifier: str
    new_password: str


class UserUpdate(BaseModel):
    name: str
    city: str
    state: str
    profession: str
    language: str


class ChatRequest(BaseModel):
    user_id: int
    query: str
    session_id: Optional[int] = None


class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


class ActivityCreate(BaseModel):
    actor_user_id: Optional[int] = None
    event_type: str
    detail: str


class LawyerCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    speciality: str
    location: str
    budget: str = "Moderate"
    verified: bool = False
    bio: Optional[str] = None


class LawyerUpdate(BaseModel):
    speciality: Optional[str] = None
    location: Optional[str] = None
    budget: Optional[str] = None
    verified: Optional[bool] = None
    bio: Optional[str] = None


class ContentCreate(BaseModel):
    content_type: str
    title: str
    section_code: Optional[str] = None
    year: Optional[str] = None
    file_name: Optional[str] = None
    description: str


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    section_code: Optional[str] = None
    year: Optional[str] = None
    file_name: Optional[str] = None
    description: Optional[str] = None


class BookingCreate(BaseModel):
    user_id: int
    lawyer_name: str
    case_type: str
    mode: str
    date: str
    time_slot: str
    notes: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    city: str
    state: str
    phone: Optional[str] = None
    email: Optional[str] = None
    age: int
    profession: str
    language: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
