import requests
import time
import random
from datetime import datetime

GATEWAY_URL = "http://iot_gateway:8000/sound"  # Asegúrate de que coincida con el endpoint REST en el gateway

def run():
    while True:
        data = {
            "id": 2,
            "sound_level_db": round(random.uniform(30.0, 100.0), 2),
            "max_sound_level": round(random.uniform(90.0, 120.0), 2),
            "min_sound_level": round(random.uniform(20.0, 40.0), 2),
            "duration_active_sec": random.randint(1, 10),
            "timestamp": datetime.utcnow().isoformat()
        }
        try:
            response = requests.post(GATEWAY_URL, json=data)
            print(f"[Sensor REST] Sent: {data} | Response: {response.text}", flush=True)
        except Exception as e:
            print("[Sensor REST] Error sending data:", e)
        time.sleep(5)

if __name__ == '__main__':
    run()
