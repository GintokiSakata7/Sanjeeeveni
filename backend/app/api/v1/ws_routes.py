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
