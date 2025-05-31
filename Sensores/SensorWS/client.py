import asyncio
import websockets
import json
import random
from datetime import datetime

async def connect_to_gateway(uri, retry_interval=5):
    while True:
        try:
            websocket = await websockets.connect(uri)
            print("[Sensor WS] Conectado al gateway WebSocket", flush=True)
            return websocket
        except (ConnectionRefusedError, OSError, websockets.InvalidURI) as e:
            print(f"[Sensor WS] Esperando al gateway... ({e})", flush=True)
            await asyncio.sleep(retry_interval)

async def send_movement_data():
    uri = "ws://iot_gateway:5000/ws/movement"
    websocket = await connect_to_gateway(uri)

    try:
        while True:
            data = {
                "id": 3,
                "timestamp": datetime.utcnow().isoformat(),
                "presence": random.choice([True, False]),
                "duration_active_sec": random.randint(1, 15),
                "intensity": round(random.uniform(0.1, 1.0), 2),
                "direction": random.choice(["NORTE", "SUR", "ESTE", "OESTE", "NE", "SO", "SE", "NO"])
            }

            print(f"[Sensor WS] Sent: {json.dumps(data)}", flush=True)

            await websocket.send(json.dumps(data))
            response = await websocket.recv()
            print(f"[Sensor WS] Response: {response}", flush=True)

            await asyncio.sleep(30)
    except websockets.ConnectionClosed:
        print("[Sensor WS] Conexión cerrada. Reconectando...", flush=True)
        await send_movement_data()  # Reintenta desde el inicio si se cae la conexión

if __name__ == "__main__":
    asyncio.run(send_movement_data())
