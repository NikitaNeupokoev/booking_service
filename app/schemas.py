from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from app.models import BookingStatus, UserRole


class RoomSlotSchema(BaseModel):
    """Схема для отображения временного слота."""

    id: int
    name: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Схема для регистрации нового пользователя."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя."""

    id: int
    username: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True


class RoomCreate(BaseModel):
    """Схема для создания новой комнаты."""

    name: str
    description: Optional[str] = None
    capacity: int = Field(..., gt=0)
    time_slots: List[str]


class RoomResponse(BaseModel):
    """Схема ответа с данными комнаты."""

    id: int
    name: str
    description: Optional[str]
    capacity: int
    slots: List[RoomSlotSchema]

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    """Схема для создания бронирования."""

    room_id: int
    slot_id: int
    booking_date: date
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    """Схема ответа с деталями бронирования."""

    id: int
    room_id: int
    slot_id: int
    user_id: int
    booking_date: date
    status: BookingStatus
    notes: Optional[str]

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Схема ответа с JWT-токеном доступа."""

    access_token: str
    token_type: str = 'bearer'
