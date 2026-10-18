import asyncio
import json


class ConnectionManager:
    def __init__(self):
        self.connections = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket):
        await websocket.accept()
        async with self._lock:
            self.connections.add(websocket)

    async def disconnect(self, websocket):
        async with self._lock:
            self.connections.discard(websocket)

    async def broadcast(self, payload: dict):
        message = json.dumps(payload, default=str)
        async with self._lock:
            connections = list(self.connections)
        for websocket in connections:
            try:
                await websocket.send_text(message)
            except Exception:
                await self.disconnect(websocket)
