import enum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRole(str, enum.Enum):
    EMPLOYEE = 'employee'
    ADMIN = 'admin'


class BookingStatus(str, enum.Enum):
    ACTIVE = 'active'
    CANCELLED = 'cancelled'


class User(Base):
    """Модель пользователя."""

    __tablename__ = 'users'

    id = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    username = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    email = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )
    hashed_password = mapped_column(
        String,
        nullable=False
    )
    full_name = mapped_column(
        String(100),
        nullable=False
    )
    role = mapped_column(
        Enum(UserRole),
        default=UserRole.EMPLOYEE,
        nullable=False
    )
    is_active = mapped_column(
        Boolean,
        default=True
    )

    bookings = relationship(
        'Booking',
        back_populates='user'
    )


class Room(Base):
    """Модель комнаты."""

    __tablename__ = 'rooms'

    id = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    name = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )
    description = mapped_column(
        String(500),
        nullable=True
    )
    capacity = mapped_column(
        Integer,
        nullable=False
    )

    slots = relationship(
        'RoomSlot',
        back_populates='room',
        cascade='all, delete-orphan'
    )
    bookings = relationship(
        'Booking',
        back_populates='room'
    )


class RoomSlot(Base):
    """Модель слота комнаты."""

    __tablename__ = 'room_slots'

    id = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    room_id = mapped_column(
        Integer,
        ForeignKey(
            'rooms.id',
            ondelete='CASCADE'
        ),
        nullable=False
    )
    name = mapped_column(
        String(20),
        nullable=False
    )

    room = relationship(
        'Room',
        back_populates='slots'
    )
    bookings = relationship(
        'Booking',
        back_populates='slot'
    )

    __table_args__ = (
        UniqueConstraint(
            'room_id',
            'name',
            name='uq_room_slot'
        ),
    )


class Booking(Base):
    """Модель бронирования."""

    __tablename__ = 'bookings'

    id = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    room_id = mapped_column(
        Integer,
        ForeignKey(
            'rooms.id',
            ondelete='CASCADE'
        ),
        nullable=False
    )
    slot_id = mapped_column(
        Integer,
        ForeignKey(
            'room_slots.id',
            ondelete='CASCADE'
        ),
        nullable=False
    )
    user_id = mapped_column(
        Integer,
        ForeignKey(
            'users.id',
            ondelete='CASCADE'
        ),
        nullable=False
    )

    booking_date = mapped_column(
        Date,
        nullable=False
    )
    status = mapped_column(
        Enum(BookingStatus),
        default=BookingStatus.ACTIVE,
        nullable=False
    )
    notes = mapped_column(
        String(200),
        nullable=True
    )
    created_at = mapped_column(
        DateTime,
        server_default=func.now()
    )

    room = relationship(
        'Room',
        back_populates='bookings'
    )
    slot = relationship(
        'RoomSlot',
        back_populates='bookings'
    )
    user = relationship(
        'User',
        back_populates='bookings'
    )
