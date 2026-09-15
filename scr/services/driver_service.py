from sqlalchemy.ext.asyncio import AsyncSession
from scr.repositories.driver_repositories import DriversRepository
from scr.schemas.driver_schemas import DriverCreate, DriverResponseSchema
from logging_log import logger


class DriverService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.drive_repo = DriversRepository(db=self.db)

    async def create_driver(self,
                            create_driver: DriverCreate
                            ) -> DriverResponseSchema:
        new_drive = await self.drive_repo.create_driver(
            driver_name=create_driver.name,
            driver_car=create_driver.car)
        await self.db.commit()
        logger.info(f'Новый водитель {new_drive} создан')
        return DriverResponseSchema.model_validate(new_drive)
