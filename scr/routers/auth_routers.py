import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from scr.db.session import get_session
from logging_log import logger

from scr.schemas.auth_schemas import UserResponseSchema, UserRegisterSchema
from scr.services.auth_service import AuthService
from scr.db.session import config
from taxi_api import security

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    '/registrate',
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema
    )
async def registrate(
    user: UserRegisterSchema,
    session: AsyncSession = Depends(get_session)
):

    service = AuthService(db=session)

    return await service.create_users(
        user=user
    )


@router.post(
    '/login',
    status_code=status.HTTP_200_OK
    )
async def login(
    response: Response,
    user: UserRegisterSchema,
    session: AsyncSession = Depends(get_session)
        ):
    service = AuthService(db=session)

    existing_user = await service.get_user_by_username(username=user.username)
    if not existing_user:
        logger.error('Пользователь не существует')
        raise HTTPException(
            status_code=401,
            detail='Пользователь не найден. Зарегистрируйтесь'
            )

    user_id = existing_user.id
    user_password = existing_user.password
    if not bcrypt.checkpw(
        user.password.encode('utf-8'),
        user_password.encode('utf-8')
    ):
        logger.error('Не верный пароль')
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Неверный пароль'
            )
    token = security.create_access_token(uid=str(user_id))
    logger.info('Токен выдан')
    response.set_cookie(
        key=config.JWT_ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,
        samesite='lax',
        )
    logger.info('Успешный вход')
    return {"message": "Успешный вход"}


@router.get('/users/me',
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(security.access_token_required)]
            )
async def users_me():
    logger.info('Вы авторизованы')
    return {'data': 'Вы авторизованы'}


@router.post('/logout',
             status_code=status.HTTP_200_OK
             )
async def logout(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    logger.info('Пользователь вышел из системы')
    return {"message": "Вы вышли из системы"}
