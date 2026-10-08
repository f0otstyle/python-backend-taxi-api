from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from logging_log import log, logger
from scr.db.session import get_session


from scr.schemas.driver_schemas import (DriverCreate,
                                        DriverUpdate,
                                        DriverUpdateStatusSchema)
from scr.services.driver_service import DriverService
from scr.auth.security import security

router = APIRouter(prefix="/drivers")


@router.post('/', status_code=status.HTTP_201_CREATED)
@log
async def create_driver(
    driver: DriverCreate,
    session: AsyncSession = Depends(get_session)
        ):
    try:
        service = DriverService(db=session)
        return await service.create_driver(driver)
    except SQLAlchemyError:
        logger.exception('Ошибка не подключения к бд')
        raise HTTPException(status_code=500, detail="Ошибка базы данных")


@router.post('/status/{driver_id}', status_code=status.HTTP_200_OK)
@log
async def update_status_drivers(
    driver_id: int,
    driver: DriverUpdateStatusSchema,
    session: AsyncSession = Depends(get_session)
        ):
    try:
        service = DriverService(db=session)
        return await service.update_status(
            driver_id=driver_id,
            status=driver.status,
            lat=driver.lat,
            lon=driver.lon
            )
    except SQLAlchemyError:
        logger.exception('Ошибка не подключения к бд')
        raise HTTPException(status_code=500, detail="Ошибка базы данных")


@router.post('/location/{driver_id}', status_code=status.HTTP_200_OK)
@log
async def update_drivers_location(
    driver_id: int,
    driver: DriverUpdate,
    session: AsyncSession = Depends(get_session)
        ):
    try:
        service = DriverService(db=session)
        return await service.update_local(
            driver_id=driver_id,
            lat=driver.lat,
            lon=driver.lon
        )
    except SQLAlchemyError:
        logger.exception('Ошибка не подключения к бд')
        raise HTTPException(status_code=500, detail="Ошибка базы данных")


@router.get('/{driver_id}', status_code=status.HTTP_200_OK)
@log
async def get_drivers_driver_id(
    driver_id: int,
    session: AsyncSession = Depends(get_session)
        ):
    try:
        service = DriverService(db=session)
        get_drivers = await service.get_driver_id(driver_id)
        if get_drivers:
            return get_drivers
    except SQLAlchemyError:
        logger.exception('Ошибка не подключения к бд')
        raise HTTPException(status_code=500, detail="Ошибка базы данных")
