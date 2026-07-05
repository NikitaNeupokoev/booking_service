from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import (
    create_user,
    get_user_by_username
)
from app.database import get_db
from app.models import User
from app.schemas import (
    Token,
    UserCreate,
    UserResponse
)
from app.security import (
    create_access_token,
    verify_password
)

router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post('/login', response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_username(
        db,
        form_data.username
    )
    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        """Аутентификация пользователя и выдача токена."""
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный логин или пароль',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = create_access_token(
        data={'sub': str(user.id)}
    )
    return Token(
        access_token=access_token,
        token_type='bearer'
    )


@router.post(
    '/register',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя."""
    existing_user = await get_user_by_username(
        db, user_data.username
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Имя пользователя занято'
        )

    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email уже зарегистрирован'
        )

    return await create_user(db, user_data)
