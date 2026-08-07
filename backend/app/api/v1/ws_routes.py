from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

from app.ws_manager import manager

router = APIRouter(prefix="/ws", tags=["WebSockets"])
logger = logging.getLogger(__name__)

@router.websocket("/sos/{sos_id}")
async def websocket_sos_endpoint(websocket: WebSocket, sos_id: str):
    """WebSocket endpoint for the patient/citizen web app to receive live updates and WebRTC calls."""
    await manager.connect_sos(websocket, sos_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")
            
            # WebRTC Signaling from Patient to Doctor
            if msg_type in ["CALL_ANSWER", "CALL_REJECT", "CALL_END", "ICE_CANDIDATE"]:
                doctor_id = message.get("doctor_id")
                if doctor_id:
                    # Relay to the specific doctor handling this case
                    await manager.broadcast_to_doctor(doctor_id, {
                        "type": msg_type,
                        "sos_id": sos_id,
                        **message
                    })
    except WebSocketDisconnect:
        manager.disconnect_sos(websocket, sos_id)
    except Exception as e:
        logger.error(f"SOS WS Error: {e}")
        manager.disconnect_sos(websocket, sos_id)

@router.websocket("/doctor/{doctor_id}")
async def websocket_doctor_endpoint(websocket: WebSocket, doctor_id: str):
    """WebSocket endpoint for the doctor mobile app to receive assigned cases and WebRTC calls."""
    await manager.connect_doctor(websocket, doctor_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")
            
            # When doctor initiates a call or sends ICE candidates, relay to patient
            if msg_type in ["INITIATE_CALL", "CALL_END", "ICE_CANDIDATE"]:
                sos_id = message.get("sos_id")
                if sos_id:
                    # Remember which case the doctor is currently handling
                    manager.doctor_current_case[doctor_id] = sos_id
                    
                    # Relay to the specific SOS case patient
                    await manager.broadcast_to_sos(sos_id, {
                        "type": msg_type,
                        "doctor_id": doctor_id,
                        **message
                    })
                    
    except WebSocketDisconnect:
        manager.disconnect_doctor(websocket, doctor_id)
    except Exception as e:
        logger.error(f"Doctor WS Error: {e}")
        manager.disconnect_doctor(websocket, doctor_id)


@router.websocket("/driver/{driver_id}")
async def websocket_driver_endpoint(websocket: WebSocket, driver_id: str):
    """WebSocket endpoint for the driver mobile app to receive task assignments and send status updates.
    
    Message types (Driver → Server):
        TASK_ACCEPTED  - Driver accepts a pending task
        TASK_REJECTED  - Driver rejects a pending task
        TASK_COMPLETED - Driver marks task as complete
        LOCATION_UPDATE - Driver sends GPS coordinates
    
    Message types (Server → Driver):
        NEW_TASK_ASSIGNED - Hospital assigned a new pickup task
    """
    await manager.connect_driver(websocket, driver_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")
            
            if msg_type == "LOCATION_UPDATE":
                # Driver is sharing GPS location — relay to the SOS patient tracker
                sos_id = message.get("sos_id")
                if sos_id:
                    await manager.broadcast_to_sos(sos_id, {
                        "type": "DRIVER_LOCATION",
                        "driver_id": driver_id,
                        "latitude": message.get("latitude"),
                        "longitude": message.get("longitude"),
                    })
            
            elif msg_type in ["TASK_ACCEPTED", "TASK_REJECTED", "TASK_COMPLETED"]:
                # Relay driver actions to the SOS patient tracker
                sos_id = message.get("sos_id")
                if sos_id:
                    await manager.broadcast_to_sos(sos_id, {
                        "type": msg_type,
                        "driver_id": driver_id,
                        "sos_id": sos_id,
                        "message": message.get("message", "")
                    })
                    
    except WebSocketDisconnect:
        manager.disconnect_driver(websocket, driver_id)
    except Exception as e:
        logger.error(f"Driver WS Error: {e}")
        manager.disconnect_driver(websocket, driver_id)


@router.websocket("/helper/{helper_id}")
async def websocket_helper_endpoint(websocket: WebSocket, helper_id: str):
    """WebSocket endpoint for the helper mobile app to receive SOS-based notifications.
    
    Message types (Helper → Server):
        ALERT_ACCEPTED - Helper accepts an SOS alert
        ALERT_REJECTED - Helper rejects an SOS alert
    
    Message types (Server → Helper):
        SOS_ALERT - New SOS nearby with disease + coordinates
    """
    await manager.connect_helper(websocket, helper_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")
            
            if msg_type in ["ALERT_ACCEPTED", "ALERT_REJECTED"]:
                # Relay helper response to SOS patient tracker
                sos_id = message.get("sos_id")
                if sos_id:
                    await manager.broadcast_to_sos(sos_id, {
                        "type": f"HELPER_{msg_type.split('_')[1]}",
                        "helper_id": helper_id,
                        "sos_id": sos_id,
                        "message": message.get("message", "")
                    })
                    
    except WebSocketDisconnect:
        manager.disconnect_helper(websocket, helper_id)
    except Exception as e:
        logger.error(f"Helper WS Error: {e}")
        manager.disconnect_helper(websocket, helper_id)


# --- Standalone WebRTC Test Module Integration ---
test_clients = set()

@router.websocket("/test")
async def websocket_test_endpoint(websocket: WebSocket):
    """Simple broadcast WebSocket endpoint for the standalone test module."""
    await websocket.accept()
    test_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to all other connected test clients
            for client in test_clients.copy():
                if client != websocket:
                    try:
                        await client.send_text(data)
                    except Exception:
                        pass
    except WebSocketDisconnect:
        test_clients.remove(websocket)
    except Exception as e:
        logger.error(f"Test WS Error: {e}")
        if websocket in test_clients:
            test_clients.remove(websocket)

