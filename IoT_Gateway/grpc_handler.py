import sensor_pb2
import sensor_pb2_grpc

class GRPCSensorService(sensor_pb2_grpc.SensorServiceServicer):
    def SendData(self, request, context):
        print(f"[gRPC] Received from {request.id}: {getattr(request, 'temperature', 'N/A')}°C at {request.timestamp}", flush=True)
        return sensor_pb2.SensorResponse(message="Data received via gRPC")
