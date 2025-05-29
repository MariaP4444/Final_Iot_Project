import asyncio
import websockets
import json

async def WSSensorService(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"[WebSocket] Received from sensor {data.get('id')}: {data.get('heart_rate', 'N/A')} BPM at {data.get('timestamp')}", flush=True)
            await websocket.send(json.dumps({"message": "Data received via WebSocket"}))
    except websockets.exceptions.ConnectionClosed:
        print(f"[WebSocket] Connection closed: {websocket.remote_address}", flush=True)
