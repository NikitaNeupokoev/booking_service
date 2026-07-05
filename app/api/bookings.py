from datetime import date
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import (
    cancel_booking,
    check_slot_availability,
    create_booking,
    get_booking_by_id,
    get_room_by_id,
    get_user_bookings,
)
from app.database import get_db
from app.dependencies import get_current_user
from app.models import (
    BookingStatus,
    RoomSlot,
    User,
    UserRole
)
from app.schemas import (
    BookingCreate,
    BookingResponse
)

router = APIRouter(prefix='/bookings', tags=['Bookings'])


@router.get('/', response_model=List[BookingResponse])
async def get_my_bookings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение бронирований текущего пользователя."""
    return await get_user_bookings(db, user_id=user.id)


@router.post(
    '/',
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_new_booking(
    booking_data: BookingCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создание нового бронирования."""
    room = await get_room_by_id(db, booking_data.room_id)
    if not room or not room.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Комната не найдена'
        )

    query = select(RoomSlot).where(
        RoomSlot.id == booking_data.slot_id,
        RoomSlot.room_id == booking_data.room_id
    )

    result = await db.execute(query)
    slot_exists = result.scalar_one_or_none()

    if not slot_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Слот не принадлежит этой комнате'
        )

    if booking_data.booking_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя бронировать прошедшую дату'
        )

    is_available = await check_slot_availability(
        db,
        room_id=booking_data.room_id,
        slot_id=booking_data.slot_id,
        booking_date=booking_data.booking_date
    )
    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Слот на эту дату уже занят'
        )

    return await create_booking(
        db,
        booking_data,
        user_id=user.id
    )


@router.delete(
    '/{booking_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_existing_booking(
    booking_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Отмена активного бронирования комнаты."""
    booking = await get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Бронирование не найдено'
        )

    if user.role != UserRole.ADMIN and booking.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нельзя отменить чужую бронь'
        )

    if booking.status != BookingStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Бронь уже неактивна'
        )

    await cancel_booking(db, booking_id)
    return None
