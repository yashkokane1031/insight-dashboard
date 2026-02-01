"""
WebSocket Connection Manager for Real-Time Data Streaming

This module handles multiple WebSocket connections, allowing the backend
to broadcast data updates to all connected clients instantly.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time data broadcasting.
    
    Features:
    - Track active connections
    - Broadcast messages to all connected clients
    - Handle graceful disconnects
    """
    
    def __init__(self):
        # List of active WebSocket connections
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection and add it to the active list."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from the active list."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific client."""
        await websocket.send_text(message)
    
    async def broadcast(self, data: dict):
        """
        Broadcast a message to ALL connected clients.
        
        Args:
            data: Dictionary to be serialized as JSON and sent to all clients
        """
        message = json.dumps(data)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                disconnected.append(connection)
        
        # Clean up any failed connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_data_point(self, data_point: dict):
        """
        Convenience method to broadcast a new data point.
        
        Args:
            data_point: DataPoint dict with id, name, value, timestamp
        """
        await self.broadcast({
            "type": "new_data",
            "payload": data_point
        })
    
    @property
    def connection_count(self) -> int:
        """Return the number of active connections."""
        return len(self.active_connections)


# Global instance to be used across the application
manager = ConnectionManager()
