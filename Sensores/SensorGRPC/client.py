import grpc
import time
import random
from datetime import datetime

import sensor_pb2
import sensor_pb2_grpc

def run():
    # 'iot_gateway' es el nombre del servicio del gateway en docker-compose
    channel = grpc.insecure_channel('iot_gateway:50051')
    stub = sensor_pb2_grpc.SensorServiceStub(channel)

    while True:
        data = sensor_pb2.OxygenData(
            id=1,
            heart_rate_bpm=random.randint(60, 100),
            spo2_percent=random.randint(95, 100),
            raw_ir=random.randint(20000, 25000),
            raw_red=random.randint(18000, 22000),
            timestamp=datetime.utcnow().isoformat()
        )
        print(f"[Sensor gRPC] Enviando datos: {data}", flush=True)
        response = stub.SendData(data)
        print(f"[Sensor gRPC] Respuesta del gateway: {response.message}", flush=True)
        time.sleep(5)  # Espera 5 segundos antes del siguiente envío

if __name__ == '__main__':
    run()
