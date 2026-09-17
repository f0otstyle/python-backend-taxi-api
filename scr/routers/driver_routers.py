from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from logging_log import log, logger
from scr.db.session import get_session


from scr.schemas.driver_schemas import DriverCreate
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
    