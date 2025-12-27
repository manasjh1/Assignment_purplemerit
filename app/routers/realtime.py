from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.queue_service import redis_client
from app.services.socket_service import publish_event
import asyncio
import json

router = APIRouter()

# Updated route to include user_id for tracking presence
@router.websocket("/ws/{project_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str, user_id: str):
    """
    Handles real-time collaboration with Join/Leave events.
    Satisfies 'WebSocket-based communication' and 'User join/leave' events[cite: 51, 54].
    """
    await websocket.accept()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(project_id)

    # 1. Broadcast JOIN Event 
    join_event = {
        "type": "USER_JOIN", 
        "user_id": user_id, 
        "message": f"User {user_id} entered the workspace"
    }
    await publish_event(project_id, join_event)

    try:
        while True:
            # Race condition handling: Wait for EITHER WebSocket msg OR Redis msg
            try:
                # Listen for client messages (File changes, cursor updates)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                
                # Pass through the client's specific event type
                msg_data = json.loads(data)
                # Ensure user_id is attached to the message
                msg_data["user_id"] = user_id
                await publish_event(project_id, msg_data)
                
            except asyncio.TimeoutError:
                pass # No message from client, continue to check Redis

            # Check for messages from OTHER clients (via Redis)
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_text(message['data'])
                    
    except WebSocketDisconnect:
        # 2. Broadcast LEAVE Event 
        leave_event = {
            "type": "USER_LEAVE", 
            "user_id": user_id, 
            "message": f"User {user_id} left the workspace"
        }
        await publish_event(project_id, leave_event)
        await pubsub.unsubscribe(project_id)