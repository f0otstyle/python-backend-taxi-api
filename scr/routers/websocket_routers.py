from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from scr.websocket.manager import ConnectionManager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/driver/{driver_id}")
async def websocket_endpoint(websocket: WebSocket, driver_id: int):
    manager = ConnectionManager()
    await manager.connect(websocket, driver_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Сервер получил: {data}")
    except WebSocketDisconnect:
        manager.disconnect(driver_id)
