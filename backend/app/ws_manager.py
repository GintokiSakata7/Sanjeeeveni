from fastapi import WebSocket
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps sos_id -> list of patient/citizen connections
        self.active_sos_connections: Dict[str, List[WebSocket]] = {}
        # Maps doctor_id -> list of doctor app connections
        self.active_doctor_connections: Dict[str, List[WebSocket]] = {}
        # Maps driver_id -> list of driver app connections
        self.active_driver_connections: Dict[str, List[WebSocket]] = {}
        # Maps helper_id -> list of helper app connections
        self.active_helper_connections: Dict[str, List[WebSocket]] = {}
        # Keep track of which sos_id a doctor is currently handling (for routing ICE candidates)
        # map: doctor_id -> current_sos_id
        self.doctor_current_case: Dict[str, str] = {}

    # ─── SOS (Patient/Citizen) ────────────────────────────────

    async def connect_sos(self, websocket: WebSocket, sos_id: str):
        await websocket.accept()
        if sos_id not in self.active_sos_connections:
            self.active_sos_connections[sos_id] = []
        self.active_sos_connections[sos_id].append(websocket)
        logger.info(f"SOS {sos_id} connected. Total: {len(self.active_sos_connections[sos_id])}")

    def disconnect_sos(self, websocket: WebSocket, sos_id: str):
        if sos_id in self.active_sos_connections:
            if websocket in self.active_sos_connections[sos_id]:
                self.active_sos_connections[sos_id].remove(websocket)
            if not self.active_sos_connections[sos_id]:
                del self.active_sos_connections[sos_id]
        logger.info(f"SOS {sos_id} disconnected.")

    async def broadcast_to_sos(self, sos_id: str, message: dict):
        """Send message to all clients connected to a specific SOS ID"""
        if sos_id in self.active_sos_connections:
            message_str = json.dumps(message)
            for connection in self.active_sos_connections[sos_id]:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    logger.error(f"Error sending to SOS {sos_id}: {e}")

    # ─── Doctor ───────────────────────────────────────────────

    async def connect_doctor(self, websocket: WebSocket, doctor_id: str):
        await websocket.accept()
        if doctor_id not in self.active_doctor_connections:
            self.active_doctor_connections[doctor_id] = []
        self.active_doctor_connections[doctor_id].append(websocket)
        logger.info(f"Doctor {doctor_id} connected. Total: {len(self.active_doctor_connections[doctor_id])}")

    def disconnect_doctor(self, websocket: WebSocket, doctor_id: str):
        if doctor_id in self.active_doctor_connections:
            if websocket in self.active_doctor_connections[doctor_id]:
                self.active_doctor_connections[doctor_id].remove(websocket)
            if not self.active_doctor_connections[doctor_id]:
                del self.active_doctor_connections[doctor_id]
        if doctor_id in self.doctor_current_case:
            del self.doctor_current_case[doctor_id]
        logger.info(f"Doctor {doctor_id} disconnected.")

    async def broadcast_to_doctor(self, doctor_id: str, message: dict):
        """Send message to a specific doctor's devices"""
        if doctor_id in self.active_doctor_connections:
            message_str = json.dumps(message)
            for connection in self.active_doctor_connections[doctor_id]:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    logger.error(f"Error sending to Doctor {doctor_id}: {e}")

    # ─── Driver ───────────────────────────────────────────────

    async def connect_driver(self, websocket: WebSocket, driver_id: str):
        await websocket.accept()
        if driver_id not in self.active_driver_connections:
            self.active_driver_connections[driver_id] = []
        self.active_driver_connections[driver_id].append(websocket)
        logger.info(f"Driver {driver_id} connected. Total: {len(self.active_driver_connections[driver_id])}")

    def disconnect_driver(self, websocket: WebSocket, driver_id: str):
        if driver_id in self.active_driver_connections:
            if websocket in self.active_driver_connections[driver_id]:
                self.active_driver_connections[driver_id].remove(websocket)
            if not self.active_driver_connections[driver_id]:
                del self.active_driver_connections[driver_id]
        logger.info(f"Driver {driver_id} disconnected.")

    async def broadcast_to_driver(self, driver_id: str, message: dict):
        """Send message to a specific driver's devices"""
        if driver_id in self.active_driver_connections:
            message_str = json.dumps(message)
            for connection in self.active_driver_connections[driver_id]:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    logger.error(f"Error sending to Driver {driver_id}: {e}")

    # ─── Helper ───────────────────────────────────────────────

    async def connect_helper(self, websocket: WebSocket, helper_id: str):
        await websocket.accept()
        if helper_id not in self.active_helper_connections:
            self.active_helper_connections[helper_id] = []
        self.active_helper_connections[helper_id].append(websocket)
        logger.info(f"Helper {helper_id} connected. Total: {len(self.active_helper_connections[helper_id])}")

    def disconnect_helper(self, websocket: WebSocket, helper_id: str):
        if helper_id in self.active_helper_connections:
            if websocket in self.active_helper_connections[helper_id]:
                self.active_helper_connections[helper_id].remove(websocket)
            if not self.active_helper_connections[helper_id]:
                del self.active_helper_connections[helper_id]
        logger.info(f"Helper {helper_id} disconnected.")

    async def broadcast_to_helper(self, helper_id: str, message: dict):
        """Send message to a specific helper's devices"""
        if helper_id in self.active_helper_connections:
            message_str = json.dumps(message)
            for connection in self.active_helper_connections[helper_id]:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    logger.error(f"Error sending to Helper {helper_id}: {e}")

manager = ConnectionManager()

