# from datetime import datetime, timedelta, timezone
# from decimal import Decimal
# from sqlalchemy.ext.asyncio import (create_async_engine,
#                                     AsyncSession,
#                                     async_sessionmaker)
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# from sqlalchemy import ForeignKey, String, Numeric, TIMESTAMP, select, and_
# from sqlalchemy.sql import func
# from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# from typing import Annotated
# from fastapi import FastAPI, HTTPException, Request, Header, Depends, Response
# from http import HTTPStatus
# from fastapi.encoders import jsonable_encoder
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel
# from contextlib import asynccontextmanager
# from error_handler import OrderError, SearchError
# from logging_log import logger, log
# from authx import AuthXConfig, AuthX, TokenPayload
# import asyncio
# import asyncpg
# import bcrypt
# import os


# DB_HOST = os.getenv('DB_HOST', 'localhost')
# DB_PORT = int(os.getenv('DB_PORT', 5432))
# DB_USER = os.getenv('POSTGRES_USER', 'pgAdmin')
# DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
# DB_NAME = os.getenv('POSTGRES_DB', 'taxi_db')

# TIME = 5

# DATABASE_URL_asyncpg = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# async_engine = create_async_engine(DATABASE_URL_asyncpg, echo=True)
# Async_sessionmaker_local = async_sessionmaker(async_engine,
#                                               class_=AsyncSession,
#                                               expire_on_commit=False
#                                               )

# str_256 = Annotated[str, String(256)]
# money_money = Annotated[Decimal, Numeric(10, 2)]


# class Base(DeclarativeBase):
#     pass


# class AuthORM(Base):
#     __tablename__ = 'users'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str_256] = mapped_column(nullable=False)
#     password: Mapped[str_256] = mapped_column(nullable=False)


# class DriverORM(Base):
#     __tablename__ = 'drivers'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str_256] = mapped_column(nullable=False)
#     car: Mapped[str_256] = mapped_column(nullable=False)
#     money: Mapped[money_money] = mapped_column(nullable=False, default=0)


# class OrderTaxiORM(Base):
#     __tablename__ = 'order_taxi'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     idempotency_key: Mapped[str_256] = mapped_column(
#         nullable=False,
#         unique=True)
#     from_address: Mapped[str_256]
#     to_address: Mapped[str_256] = mapped_column(nullable=False)
#     price: Mapped[money_money] = mapped_column(nullable=False)
#     created_at: Mapped[datetime] = mapped_column(TIMESTAMP,
#                                                  server_default=func.now()
#                                                  )
#     driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"),
#                                            nullable=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),
#                                          nullable=False)


# class RidesTaxiORM(Base):
#     __tablename__ = 'rides'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     order_id: Mapped[int] = mapped_column(ForeignKey("order_taxi.id",
#                                                      ondelete="CASCADE"),
#                                                      nullable=False)
#     driver_id: Mapped[int | None] = mapped_column(ForeignKey("drivers.id"),
#                                            nullable=True)
#     started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),
#                                                  server_default=func.now())
#     finished_at: Mapped[datetime | None] = mapped_column(
#         TIMESTAMP(timezone=True),
#         nullable=True)
#     duration: Mapped[int] = mapped_column(nullable=True)


# class TaxiCardORM(Base):
#     __tablename__ = 'taxi_card'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),
#                                          unique=True
#                                          )
#     balance: Mapped[money_money] = mapped_column(nullable=False,
#                                                  default=0
#                                                  )


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     await async_engine.dispose()

# app = FastAPI(lifespan=lifespan)


# async def get_session():
#     async with Async_sessionmaker_local() as session:
#         try:
#             yield session
#         finally:
#             await session.close()


# config = AuthXConfig(
#     JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'SECRET-KEY'),
#     JWT_TOKEN_LOCATION=['cookies'],
#     JWT_ACCESS_COOKIE_NAME='my_cookie',
#     JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=1),
#     JWT_COOKIE_CSRF_PROTECT=False,
#     )


# security: AuthX = AuthX(config=config)


# class OrderCreate(BaseModel):
#     from_address: str
#     to_address: str
#     price: Decimal


# class UserRegisterSchema(BaseModel):
#     username: str
#     password: str


# class DriverCreate(BaseModel):
#     name: str
#     car: str


# class MoneySchema(BaseModel):
#     money: Decimal


# @app.exception_handler(OrderError)
# async def order_error(request: Request, exc: OrderError):
#     return JSONResponse(
#         status_code=HTTPStatus.CONFLICT,
#         content={
#             "error": True,
#             "type": "OrderError",
#             'detail': exc.detail
#         })


# @app.exception_handler(SearchError)
# async def search_error(request: Request, exc: SearchError):
#     return JSONResponse(
#         status_code=HTTPStatus.NOT_FOUND,
#         content={
#             "error": True,
#             "type": "SearchError",
#             'detail': exc.detail
#         })


# @app.post('/registrate', status_code=HTTPStatus.CREATED)
# async def registrate(
#     user: UserRegisterSchema,
#     session: AsyncSession = Depends(get_session)
#         ):
#     username = user.username
#     existing = await session.scalar(
#         select(AuthORM).where(AuthORM.name == username)
#         )

#     if existing:
#         logger.error('Пользователь уже существует')
#         raise HTTPException(
#             status_code=400,
#             detail='Пользователь уже существует'
#             )
#     salt = bcrypt.gensalt()
#     hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt).decode('utf-8')
#     logger.info('Пароль захеширован')

#     new_user = AuthORM(name=username, password=hashed_password)
#     session.add(new_user)
#     await session.commit()
#     logger.info(f'Пользователь создан {new_user}')
#     return {"message": "Пользователь создан"}


# @app.post('/login', status_code=HTTPStatus.OK)
# async def login(
#     response: Response,
#     user: UserRegisterSchema,
#     session: AsyncSession = Depends(get_session)
#         ):
#     username = user.username
#     existing = await session.scalar(
#         select(AuthORM).where(AuthORM.name == username)
#         )
#     if not existing:
#         logger.error('Пользователь не существует')
#         raise HTTPException(
#             status_code=401,
#             detail='Пользователь не найден. Зарегистрируйтесь'
#             )

#     user_id = existing.id
#     user_password = existing.password
#     if not bcrypt.checkpw(
#         user.password.encode('utf-8'),
#         user_password.encode('utf-8')
#     ):
#         logger.error('Не верный пароль')
#         raise HTTPException(
#                 status_code=HTTPStatus.UNAUTHORIZED,
#                 detail='Неверный пароль'
#             )
#     token = security.create_access_token(uid=str(user_id))
#     logger.info('Токен выдан')
#     response.set_cookie(
#         key=config.JWT_ACCESS_COOKIE_NAME,
#         value=token,
#         httponly=True,
#         secure=True,
#         samesite='lax',
#         )
#     logger.info('Успешный вход')
#     return {"message": "Успешный вход"}


# @app.get('/users/me',
#          status_code=HTTPStatus.OK,
#          dependencies=[Depends(security.access_token_required)]
#          )
# async def users_me():
#     logger.info('Вы авторизованы')
#     return {'data': 'Вы авторизованы'}


# @app.post('/logout', status_code=HTTPStatus.OK)
# async def logout(response: Response):
#     response.delete_cookie("my_cookie")
#     logger.info('Вы вышли из системы')
#     return {"message": "Вы вышли из системы"}


# @app.post('/drivers', status_code=HTTPStatus.CREATED)
# @log
# async def create_driver(
#     driver: DriverCreate,
#     session: AsyncSession = Depends(get_session)
#         ):
#     '''Добавляем нового водителя'''
#     driver_name = driver.name
#     driver_car = driver.car
#     try:
#         new_driver = DriverORM(name=driver_name, car=driver_car)
#         session.add(new_driver)
#         await session.commit()
#         await session.refresh(new_driver)
#         logger.info(f'Водитель создан: {new_driver.name}')
#         return {
#             "id": new_driver.id,
#             "name": new_driver.name,
#             "car": new_driver.car,
#             "money": str(new_driver.money)
#         }
#     except SQLAlchemyError:
#         logger.exception('Ошибка не подключения к бд')
#         raise HTTPException(status_code=500, detail="Ошибка базы данных")


# @app.get('/taxi', status_code=HTTPStatus.OK)
# @log
# async def list_of_orders(session: AsyncSession = Depends(get_session)):
#     '''Список всех заказов'''
#     try:
#         result = await session.execute(select(OrderTaxiORM))
#         rows = result.scalars().all()
#         if rows:
#             return [{
#                 'id': row.id,
#                 'idempotency_key': row.idempotency_key,
#                 'to_address': row.to_address,
#                 'price': str(row.price),
#                 'created_at': row.created_at
#             } for row in rows]
#         logger.error('База данных пуста')
#         return []
#     except SQLAlchemyError:
#         logger.exception('Ошибка не подключения к бд')
#         raise HTTPException(status_code=500, detail="Ошибка базы данных")


# @app.post('/taxi',
#           status_code=HTTPStatus.CREATED,
#           dependencies=[Depends(security.access_token_required)])
# @log
# async def ordering_a_taxi(
#     orders: OrderCreate,
#     request: Request,
#     idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
#     session: AsyncSession = Depends(get_session),
#     token_data: TokenPayload = Depends(security.access_token_required)
#         ):
#     '''Создаем заказ'''
#     user_id = int(token_data.sub)
#     from_address = orders.from_address
#     to_address = orders.to_address
#     price = orders.price

#     if not idempotency_key:
#         raise HTTPException(
#             status_code=HTTPStatus.BAD_REQUEST,
#             detail="Поле 'idempotency_key' обязательно"
#         )
#     existing = await session.scalar(
#         select(OrderTaxiORM).where(
#             OrderTaxiORM.idempotency_key == idempotency_key
#             )
#         )

#     if existing:
#         logger.info(f"Повторный запрос с ключом {idempotency_key}")
#         return JSONResponse(
#             status_code=HTTPStatus.CREATED,
#             content=jsonable_encoder({
#                     'id': existing.id,
#                     'from_address': existing.from_address,
#                     'to_address': existing.to_address,
#                     'price': existing.price,
#                     'user_id': existing.user_id,
#                     'driver_id': existing.driver_id,
#                     'created_at': existing.created_at
#             }),
#             headers={"Location": f"/taxi/{existing.id}"}
#         )
#     current_time = datetime.now(timezone.utc).timestamp()
#     duplicate = await session.scalar(select(OrderTaxiORM).where(
#         and_(
#             OrderTaxiORM.to_address == to_address,
#             OrderTaxiORM.user_id == user_id
#         )
#     ).order_by(OrderTaxiORM.created_at.desc()))

#     if duplicate:
#         created_at = duplicate.created_at.timestamp()
#         time_diff = current_time - created_at
#         if time_diff < TIME:
#             logger.warning(
#                 f'Попытка создать дубликат заказа для {to_address} (прошло {time_diff:.1f} с)'
#                 )
#             raise OrderError()
#     logger.info('Можно сделать новый заказ')
#     try:
#         new_order = OrderTaxiORM(
#             idempotency_key=idempotency_key,
#             from_address=from_address,
#             to_address=to_address,
#             price=price,
#             user_id=user_id
#             )
#         session.add(new_order)
#         await session.flush()

#     except IntegrityError:
#         await session.rollback()
#         raise HTTPException(status_code=409,
#                             detail="Конфликт при создании заказа"
#                             )

#     appoint = await taxi_to_appoint(new_order.id, session)
#     if not appoint:
#         await session.rollback()
#         logger.warning(f'Не удалось создать заказ {new_order.id}: нет свободных водителей')
#         raise HTTPException(
#             status_code=HTTPStatus.SERVICE_UNAVAILABLE,
#             detail="В данный момент нет свободных водителей"
#         )

#     drive = await taxi_ride(new_order.id, session)
#     if not drive:
#         await session.rollback()
#         logger.error(f'Поездка не состоялась по заказу {new_order.id}')
#         raise HTTPException(status_code=500,
#                             detail="Ошибка при обработке поездки"
#                             )
#     pay = await pay_to_taxi(new_order.id, session)
#     if not pay:
#         await session.rollback()
#         logger.warning(f'Заказ {new_order.id} отменен: оплата не прошла')
#         raise HTTPException(
#             status_code=HTTPStatus.PAYMENT_REQUIRED,
#             detail="Недостаточно средств на карте для оплаты поездки"
#         )
#     await session.commit()
#     logger.info(f'Заказ {new_order.id} успешно создан, выполнен и оплачен')

#     logger.info(f'Новый заказ сделан с ID {new_order.id}')
#     return JSONResponse(
#             status_code=HTTPStatus.CREATED,
#             content=jsonable_encoder({
#                 'id': new_order.id,
#                 'from_address': new_order.from_address,
#                 'to_address': new_order.to_address,
#                 'price': str(new_order.price),
#                 'user_id': new_order.user_id,
#                 'driver_id': new_order.driver_id,
#                 'created_at': new_order.created_at
#             }),
#             headers={"Location": f"/taxi/{new_order.id}"}
#         )


# @log
# async def taxi_to_appoint(
#     order_id: int,
#     session: AsyncSession
#         ):
#     '''Назначаем водителя для поездки'''
#     stmt = (select(DriverORM)
#             .order_by(func.random())
#             .limit(1)
#             .with_for_update(skip_locked=True)
#             )
#     driver = await session.scalar(stmt)

#     if not driver:
#         return None

#     order = await session.get(OrderTaxiORM, order_id)
#     if not order:
#         return None

#     if order.driver_id is not None:
#         return None
#     order.driver_id = driver.id

#     await session.flush()
#     await session.refresh(order)

#     return {
#         'id': order.id,
#         'from_address': order.from_address,
#         'to_address': order.to_address,
#         'price': str(order.price),
#         'user_id': order.user_id,
#         'driver_id': order.driver_id,
#         'created_at': order.created_at
#     } if order else None


# @log
# async def taxi_ride(
#     order_id: int,
#     session: AsyncSession
#         ):
#     '''Симуляция поездки'''
#     order = await session.get(OrderTaxiORM, order_id)

#     if not order:
#         logger.warning(f'Заказ {order_id} не найден или нет водителя')
#         return None

#     logger.info(f'Поездка по заказу {order_id} началась')

#     start_time = datetime.now(timezone.utc)
#     duration = 1
#     await asyncio.sleep(duration)
#     end_time = datetime.now(timezone.utc)

#     ride = RidesTaxiORM(
#         order_id=order_id,
#         driver_id=order.driver_id,
#         started_at=start_time,
#         finished_at=end_time,
#         duration=duration
#     )

#     session.add(ride)
#     await session.flush()
#     logger.info(f'Поездка по заказу {order_id} завершена за {duration} сек')

#     return {
#         "order_id": ride.order_id,
#         "driver_id": ride.driver_id,
#         "started_at": ride.started_at,
#         "finished_at": ride.finished_at,
#         "duration": ride.duration
#     }


# @log
# async def pay_to_taxi(
#     order_id: int,
#     session: AsyncSession
#         ):
#     '''Оплата поездки'''
#     order = await session.get(OrderTaxiORM, order_id)

#     if not order:
#         logger.warning(f'Заказ {order_id} не найден или нет водителя')
#         return None

#     card = await session.get(TaxiCardORM, order.user_id)

#     if not card:
#         logger.warning(f'У пользователя {order.user_id} нет карты')
#         return False

#     if card.balance < order.price:
#         logger.warning('Недостаточно средств на карте')
#         return False

#     driver = await session.get(DriverORM, order.driver_id)
#     if not driver:
#         logger.warning(f'Водитель {order.driver_id} не найден')
#         return False

#     card.balance -= order.price

#     driver.money += order.price

#     await session.flush()
#     logger.info(f'Списано {order.price} с карты пользователя {order.user_id}')
#     return True


# @app.post('/pay/{user_id}',
#           status_code=HTTPStatus.OK,
#           dependencies=[Depends(security.access_token_required)])
# async def top_up_your_card(
#     payload: MoneySchema,
#     user_id: int,
#     session: AsyncSession = Depends(get_session)
#         ):
#     try:
#         money = payload.money
#         card = await session.get(TaxiCardORM, user_id)
#         if card:
#             card.balance += money
#             await session.commit()
#         else:
#             new_card = TaxiCardORM(user_id=user_id, balance=money)

#             session.add(new_card)
#             await session.commit()

#             logger.info(f'Баланс пользователя {user_id} пополнен на {money}')
#             return {"message": f"Баланс пополнен на {money}"}

#     except IntegrityError:
#         raise HTTPException(status_code=500, detail="Пользователь не найден")
#     except Exception:
#         logger.exception("Неожиданная ошибка")
#         raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


# @app.get('/taxi/{order_id}',
#          status_code=HTTPStatus.OK,
#          dependencies=[Depends(security.access_token_required)]
#          )
# @log
# async def order_search(
#     order_id: int,
#     session: AsyncSession = Depends(get_session)
#         ):
#     '''Поиск конкретного заказа'''
#     existing = await session.get(OrderTaxiORM, order_id)
#     if existing:
#         logger.info(f'Заказ по {existing.id} найден')
#         return JSONResponse(
#             status_code=HTTPStatus.OK,
#             content=jsonable_encoder({
#                 'id': existing.id,
#                 'from_address': existing.from_address,
#                 'to_address': existing.to_address,
#                 'price': existing.price,
#                 'user_id': existing.user_id,
#                 'driver_id': existing.driver_id,
#                 'created_at': existing.created_at}),
#             headers={"Location": f"/taxi/{existing.id}"}
#             )
#     logger.warning(f'Попытка найти несуществующий заказ {order_id}')
#     raise SearchError()


# @app.delete('/taxi/{order_id}',
#             status_code=HTTPStatus.NO_CONTENT,
#             dependencies=[Depends(security.access_token_required)]
#             )
# @log
# async def order_delete(
#     order_id: int,
#     session: AsyncSession = Depends(get_session)
#         ):
#     '''Удаление заказа'''
#     existing = await session.get(OrderTaxiORM, order_id)
#     if not existing:
#         raise SearchError()

#     await session.delete(existing)
#     await session.commit()
#     logger.info(f'Заказ {existing.id} удален')
#     return


# @app.get('/history',
#          status_code=HTTPStatus.OK,
#          dependencies=[Depends(security.access_token_required)])
# @log
# async def history_order_taxi(session: AsyncSession = Depends(get_session)):
#     result = await session.execute(select(OrderTaxiORM).order_by(OrderTaxiORM.created_at.desc()))
#     rows = result.scalars().all()
#     return [{
#         'id': row.id,
#         'from_address': row.from_address,
#         'to_address': row.to_address,
#         'price': str(row.price),
#         'user_id': row.user_id,
#         'driver_id': row.driver_id,
#         'created_at': row.created_at}
#         for row in rows]
