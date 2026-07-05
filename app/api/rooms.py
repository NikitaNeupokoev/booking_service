from datetime import date
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import (
    create_room,
    get_room_by_id,
    get_room_by_name,
    get_rooms
)
from app.database import get_db
from app.dependencies import (
    get_current_admin,
    get_current_user
)
from app.models import (
    Booking,
    BookingStatus,
    User
)
from app.schemas import RoomCreate, RoomResponse

router = APIRouter(prefix='/rooms', tags=['Rooms'])


@router.get('/', response_model=List[RoomResponse])
async def get_all_rooms(
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """Получение списка всех комнат."""
    return await get_rooms(db, is_active=is_active)


@router.get('/{room_id}', response_model=RoomResponse)
async def get_single_room(
    room_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение информации о конкретной комнате."""
    room = await get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Комната не найдена'
        )
    return room


@router.post(
    '/',
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_new_room(
    room_data: RoomCreate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Создание новой комнаты."""
    existing = await get_room_by_name(db, room_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Комната с таким именем уже есть'
        )
    return await create_room(db, room_data)


@router.get('/{room_id}/availability')
async def check_room_availability(
    room_id: int,
    booking_date: date,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Проверка доступности слотов."""
    room = await get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Комната не найдена'
        )

    query = select(Booking.slot_id).where(
        Booking.room_id == room_id,
        Booking.booking_date == booking_date,
        Booking.status == BookingStatus.ACTIVE
    )
    result = await db.execute(query)
    booked_slot_ids = set(result.scalars().all())

    availability = []
    for slot in room.slots:
        availability.append({
            'slot_id': slot.id,
            'time_slot': slot.name,
            'is_available': slot.id not in booked_slot_ids
        })

    return {
        'room_id': room_id,
        'room_name': room.name,
        'date': booking_date.isoformat(),
        'availability': availability
    }


@router.delete(
    '/{room_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_existing_room(
    room_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Удаление комнаты."""
    room = await get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Комната не найдена'
        )

    query = select(Booking).where(
        Booking.room_id == room_id,
        Booking.status == BookingStatus.ACTIVE,
        Booking.booking_date >= date.today()
    )

    result = await db.execute(query)

    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                'Нельзя удалить комнату, на которую '
                'есть активные бронирования'
            )
        )

    await db.delete(room)
    await db.commit()
    return None
