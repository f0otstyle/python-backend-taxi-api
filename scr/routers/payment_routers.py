from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from authx import TokenPayload

from logging_log import log, logger
from scr.db.session import get_session

from scr.services.payment_service import PaymentService
from scr.schemas.payment_schemas import MoneySchema
from scr.auth.security import security

router = APIRouter(prefix="/pay", tags=["Taxi Orders"])


@router.post('/top-up',
             status_code=status.HTTP_200_OK)
@log
async def top_up_your_card(
    payload: MoneySchema,
    session: AsyncSession = Depends(get_session),
    token_data: TokenPayload = Depends(security.access_token_required)
        ):
    try:
        user_id = int(token_data.sub)
        service = PaymentService(db=session)
        card = await service.top_up_balance(
            user_id=user_id,
            payment=payload
            )

        if card:
            logger.info(
                f'Баланс пользователя {user_id} пополнен на {payload.money}'
                )
            return {"message": f"Баланс пополнен на {payload.money}"}

    except IntegrityError:
        raise HTTPException(status_code=500, detail="Пользователь не найден")
    except Exception as e:
        logger.exception(f"Неожиданная ошибка {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
