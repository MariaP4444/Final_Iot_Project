import grpc
import time
import random
from datetime import datetime
import json

import sensor_pb2
import sensor_pb2_grpc


def create_stub(address="iot_gateway:50051", timeout=5):
    channel = grpc.insecure_channel(address)
    grpc.channel_ready_future(channel).result(timeout=timeout)
    return sensor_pb2_grpc.SensorServiceStub(channel)


def send_sensor_data(stub):
    data = sensor_pb2.OxygenData(
        id=1,
        heart_rate_bpm=random.randint(60, 100),
        spo2_percent=random.randint(95, 100),
        raw_ir=random.randint(20000, 25000),
        raw_red=random.randint(18000, 22000),
        timestamp=datetime.utcnow().isoformat()
    )
    dataPrint = {
        "id": data.id,
        "heart_rate_bpm": data.heart_rate_bpm,
        "spo2_percent": data.spo2_percent,
        "raw_ir": data.raw_ir,
        "raw_red": data.raw_red,
        "timestamp": data.timestamp
    }
    print(f"[Sensor gRPC] Enviando datos: {dataPrint}", flush=True)
    response = stub.SendData(data)
    print(f"[Sensor gRPC] Respuesta del gateway: {response.message}", flush=True)


def run():
    address = "iot_gateway:50051"
    backoff = 1  # segundos iniciales de espera

    while True:
        try:
            print(f"[Sensor gRPC] Intentando conectar con {address}...", flush=True)
            stub = create_stub(address)
            print(f"[Sensor gRPC] Conexión exitosa con el gateway.", flush=True)

            # Mientras esté conectado, enviar datos cada 5 segundos
            while True:
                send_sensor_data(stub)
                time.sleep(30)

        except (grpc.FutureTimeoutError, grpc.RpcError, OSError) as e:
            print(f"[Sensor gRPC] Error de conexión: {e}. Reintentando en {backoff}s...", flush=True)
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)  # backoff exponencial (máximo 30s)


if __name__ == '__main__':
    run()
