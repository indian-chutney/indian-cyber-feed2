from fastapi import WebSocket
from typing import List
import json
import asyncio

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_incident_alert(self, incident_data: dict):
        message = json.dumps({
            "type": "incident_alert",
            "data": incident_data
        })
        await self.broadcast(message)

    async def broadcast_dashboard_update(self, dashboard_data: dict):
        message = json.dumps({
            "type": "dashboard_update",
            "data": dashboard_data
        })
        await self.broadcast(message)