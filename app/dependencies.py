import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.crud import get_user_by_id
from app.database import get_db
from app.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Проверяет JWT-токен и возвращает
    текущего пользователя.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get('sub')
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail='Невалидный токен'
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail='Ошибка авторизации'
        )

    user = await get_user_by_id(db, user_id=int(user_id))
    if user is None:
        raise HTTPException(
            status_code=401,
            detail='Пользователь не найден'
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail='Пользователь заблокирован'
        )

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Проверяет наличие прав
    администратора у пользователя.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail='Доступ только для администраторов'
        )
    return current_user
