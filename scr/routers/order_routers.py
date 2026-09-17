from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from authx import TokenPayload

from logging_log import log
from scr.db.session import get_session
from scr.services.order_service import OrderTaxiService
from scr.schemas.order_schemas import OrderCreate, OrderResponceSchema

from scr.auth.security import security

router = APIRouter(prefix="/taxi", tags=["Taxi Orders"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=OrderResponceSchema
)
async def create_taxi_order(
    order_data: OrderCreate,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    session: AsyncSession = Depends(get_session),
    token_data: TokenPayload = Depends(security.access_token_required)
) -> OrderResponceSchema:
    user_id = int(token_data.sub)

    service = OrderTaxiService(db=session)

    return await service.create_order_taxi(
        user_id=user_id,
        idempotency_key=idempotency_key,
        order_taxi_create=order_data
    )


@router.get(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
)
async def order_order_order_id(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    token_data: TokenPayload = Depends(security.access_token_required)
     ):

    service = OrderTaxiService(db=session)

    return await service.get_order_id(order_id)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_taxi_order(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    token_data: TokenPayload = Depends(security.access_token_required)
     ) -> None:

    service = OrderTaxiService(db=session)

    await service.delete_id_orders(
        order_id=order_id
    )
    return None


@router.get('/',
            status_code=status.HTTP_200_OK,
            response_model=list[OrderResponceSchema]
            )
@log
async def list_of_orders(
    session: AsyncSession = Depends(get_session),
    token_data: TokenPayload = Depends(security.access_token_required)
     ):

    service = OrderTaxiService(db=session)
    return await service.list_order()


@router.get('/history',
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(security.access_token_required)])
@log
async def history_order_taxi(
    session: AsyncSession = Depends(get_session),
    token_data: TokenPayload = Depends(security.access_token_required)
     ):

    service = service = OrderTaxiService(db=session)
    return await service.history_get()
