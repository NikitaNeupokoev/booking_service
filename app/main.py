from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import auth, bookings, rooms
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title='Booking Service',
    description='Сервис бронирования переговорных комнат в коворкинге',
    version='1.0.0',
    lifespan=lifespan,
)

app.include_router(auth.router, prefix='/api')
app.include_router(rooms.router, prefix='/api')
app.include_router(bookings.router, prefix='/api')


@app.get('/', tags=['Root'])
async def root():
    """Приветственное сообщение API."""
    return {
        'message': 'Добро пожаловать в Booking Service API!',
        'docs': '/docs'
    }


@app.get('/health', tags=['Health'])
async def health_check():
    return {'status': 'healthy'}
