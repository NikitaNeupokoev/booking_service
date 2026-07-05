from datetime import date
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Booking,
    BookingStatus,
    Room,
    RoomSlot,
    User
)
from app.schemas import (
    BookingCreate,
    RoomCreate,
    UserCreate
)
from app.security import get_password_hash


async def get_user_by_id(
    db: AsyncSession,
    user_id: int
) -> Optional[User]:
    """
    Получает пользователя из
    базы данных по его ID.
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_username(
    db: AsyncSession,
    username: str
) -> Optional[User]:
    """
    Получает пользователя из
    базы данных по его имени.
    """
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    user_data: UserCreate
) -> User:
    """
    Получает пользователя из
    базы данных по его имени.
    """
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(
            user_data.password
        )
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_rooms(
    db: AsyncSession,
    is_active: Optional[bool] = None
) -> List[Room]:
    """
    Получает список комнат со
    всеми связанными слотами.
    """
    query = select(Room)
    if is_active is not None:
        query = query.where(
            Room.is_active == is_active
        )

    result = await db.execute(
        query.options(selectinload(Room.slots))
    )
    return list(result.scalars().all())


async def get_room_by_id(
    db: AsyncSession,
    room_id: int
) -> Optional[Room]:
    """Получает конкретную комнату по её ID."""
    result = await db.execute(
        select(Room).where(
            Room.id == room_id
        ).options(selectinload(Room.slots))
    )
    return result.scalar_one_or_none()


async def get_room_by_name(
    db: AsyncSession,
    name: str
) -> Optional[Room]:
    """Получает комнату по её названию."""
    result = await db.execute(
        select(Room).where(Room.name == name)
    )
    return result.scalar_one_or_none()


async def create_room(
    db: AsyncSession,
    room_data: RoomCreate
) -> Room:
    """
    Создает комнату и генерирует
    для неё тайм-слоты.
    """
    room = Room(
        name=room_data.name,
        description=room_data.description,
        capacity=room_data.capacity
    )
    db.add(room)
    await db.flush()

    for slot_name in room_data.time_slots:
        slot = RoomSlot(
            room_id=room.id,
            name=slot_name
        )
        db.add(slot)

    await db.commit()
    await db.refresh(room)
    return room


async def get_booking_by_id(
    db: AsyncSession,
    booking_id: int
) -> Optional[Booking]:
    """Получает информацию о бронировании по ID."""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    return result.scalar_one_or_none()


async def get_user_bookings(
    db: AsyncSession,
    user_id: int
) -> List[Booking]:
    """
    Получает список бронирований
    конкретного пользователя.
    """
    result = await db.execute(
        select(Booking).where(
            Booking.user_id == user_id
        ).order_by(Booking.booking_date)
    )
    return list(result.scalars().all())


async def check_slot_availability(
    db: AsyncSession,
    room_id: int,
    slot_id: int,
    booking_date: date
) -> bool:
    """
    Проверяет, свободен ли выбранный
    слот комнаты на дату.
    """
    query = select(Booking).where(
        and_(
            Booking.room_id == room_id,
            Booking.slot_id == slot_id,
            Booking.booking_date == booking_date,
            Booking.status == BookingStatus.ACTIVE
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none() is None


async def create_booking(
    db: AsyncSession,
    booking_data: BookingCreate,
    user_id: int
) -> Booking:
    """Создает новую запись бронирования."""
    booking = Booking(
        room_id=booking_data.room_id,
        slot_id=booking_data.slot_id,
        user_id=user_id,
        booking_date=booking_data.booking_date,
        notes=booking_data.notes
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking


async def cancel_booking(
    db: AsyncSession,
    booking_id: int
) -> Optional[Booking]:
    """Переводит статус бронирования в отмененное."""
    booking = await get_booking_by_id(db, booking_id)
    if not booking:
        return None
    booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(booking)
    return booking
