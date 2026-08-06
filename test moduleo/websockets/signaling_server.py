import asyncio
import json
import os
from aiohttp import web

connected_clients = set()

# Serve the HTML client file
async def handle_index(request):
    file_path = os.path.join(os.path.dirname(__file__), 'client.html')
    return web.FileResponse(file_path)

# Handle WebSocket connections for WebRTC signaling
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    connected_clients.add(ws)
    print(f"New client connected. Total clients: {len(connected_clients)}")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                print(f"Received message type: {data.get('type')}")
                
                # Broadcast message to all OTHER clients
                for client in connected_clients:
                    if client != ws and not client.closed:
                        await client.send_str(msg.data)
            elif msg.type == web.WSMsgType.ERROR:
                print(f"WebSocket connection closed with exception {ws.exception()}")
    finally:
        connected_clients.remove(ws)
        print(f"Client disconnected. Total clients: {len(connected_clients)}")

    return ws

app = web.Application()
app.router.add_get('/', handle_index)
app.router.add_get('/ws', websocket_handler)

if __name__ == '__main__':
    print("Starting WebRTC Server (HTTP + WebSocket) on port 8080...")
    web.run_app(app, host='0.0.0.0', port=8080)
