from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from http import HTTPStatus


from scr.db.session import lifespan


from error_handler import OrderError, SearchError
from logging_log import logger

from scr.routers.auth_routers import router as auth_router
from scr.routers.order_routers import router as order_router
from scr.routers.payment_routers import router as payment_router
from scr.routers.driver_routers import router as driver_router

app = FastAPI(
    title="Taxi API Microservice",
    version="2.0.0",
    lifespan=lifespan
)


app.include_router(auth_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(driver_router)


@app.exception_handler(OrderError)
async def order_error_handler(request: Request, exc: OrderError):
    logger.warning(f"OrderError: {exc.detail}")
    return JSONResponse(
        status_code=HTTPStatus.CONFLICT,
        content={"error": True, "type": "OrderError", "detail": exc.detail}
    )


@app.exception_handler(SearchError)
async def search_error_handler(request: Request, exc: SearchError):
    logger.warning(f"SearchError: {exc.detail}")
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"error": True, "type": "SearchError", "detail": exc.detail}
    )


@app.get("/", tags=["Health"])
async def root():
    return {"message": "Taxi API is running successfully!", "status": "OK"}
