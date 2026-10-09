from typing import Dict
from logging_log import logger
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, driver_id: int):
        await websocket.accept()
        self.active_connections[driver_id] = websocket
        logger.info(f"Водитель {driver_id} подключился к WebSocket")

    def disconnect(self, driver_id: int):
        if driver_id in self.active_connections:
            del self.active_connections[driver_id]
            logger.info(f"Водитель {driver_id} отключился")

    async def send_personal_message(self, message: dict, driver_id: int):
        websocket = self.active_connections.get(driver_id)
        if websocket:
            import json
            await websocket.send_text(json.dumps(message))
        else:
            logger.warning(f"Водитель {driver_id} офлайн.")
