import asyncio
import websockets
import json
import random
from datetime import datetime

async def send_movement_data():
    uri = "ws://iot_gateway:5000/ws/movement"  # Ajusta esto al endpoint real del gateway WS

    async with websockets.connect(uri) as websocket:
        while True:
            data = {
                "id": 3,
                "timestamp": datetime.utcnow().isoformat(),
                "presence": random.choice([True, False]),
                "duration_active_sec": random.randint(1, 15),
                "intensity": round(random.uniform(0.1, 1.0), 2),
                "direction": random.choice(["NORTE", "SUR", "ESTE", "OESTE", "NE", "SO", "SE", "NO"])
            }

            print(f"[Sensor WS] Sent: {data}", flush=True)

            await websocket.send(json.dumps(data))
            response = await websocket.recv()
            print(f"[Sensor WS] Response: {response}", flush=True)

            await asyncio.sleep(60)  # cada 60 segundos

if __name__ == "__main__":
    asyncio.run(send_movement_data())
