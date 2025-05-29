import grpc
from concurrent import futures
import time
import threading
import asyncio
import websockets
from flask import Flask, request

import sensor_pb2_grpc
from grpc_handler import GRPCSensorService
from websocket_handler import WSSensorService


# mqtt_client.py
from utils.command_line_utils import CommandLineUtils
from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import json
import sys

cmdData = CommandLineUtils.parse_sample_input_pubsub()

def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)

def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print("Connection Successful with return code: {} session present: {}".format(callback_data.return_code, callback_data.session_present))

# Callback when a connection attempt fails
def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    print("Connection failed with error code: {}".format(callback_data.error))

# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(connection, callback_data):
    print("Connection closed")


def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))

def publish_to_mqtt(topic, payload_dict):
    message_json = json.dumps(payload_dict)
    print(f"[MQTT] Publishing to topic '{topic}': {message_json}")
    mqtt_connection.publish(
        topic=topic,
        payload=message_json,
        qos=mqtt.QoS.AT_LEAST_ONCE
    )

# === gRPC Server ===
class GRPCSensorServiceNoMQTT(GRPCSensorService):
    def SendData(self, request, context):
        data = {
            "id": request.id,
            "heart_rate_bpm": request.heart_rate_bpm,
            "spo2_percent": request.spo2_percent,
            "raw_ir": request.raw_ir,
            "raw_red": request.raw_red,
            "timestamp": request.timestamp
        }
        print(f"[gRPC] Received: {data}", flush=True)
        return super().SendData(request, context)

def start_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sensor_pb2_grpc.add_SensorServiceServicer_to_server(GRPCSensorServiceNoMQTT(), server)
    server.add_insecure_port('[::]:50051')
    print("[gRPC] Starting server on port 50051...", flush=True)
    server.start()
    return server

# === WebSocket Server ===
def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(WSSensorService, "0.0.0.0", 5000)
    print("[WebSocket] Starting server on port 5000...", flush=True)
    loop.run_until_complete(start_server)
    loop.run_forever()

# === REST Server (Flask) ===
app = Flask(__name__)

@app.route('/sound', methods=['POST'])
def receive_rest_data():
    data = request.json
    print(f"[REST] Received: {data}", flush=True)
    publish_to_mqtt("sensor/data", data)
    return "REST data received", 200


def start_rest_server():
    print("[REST] Starting Flask server on port 8000...", flush=True)
    app.run(host='0.0.0.0', port=8000)

# === Main ===
if __name__ == '__main__':
    proxy_options = None
    if cmdData.input_proxy_host is not None and cmdData.input_proxy_port != 0:
        proxy_options = http.HttpProxyOptions(
            host_name=cmdData.input_proxy_host,
            port=cmdData.input_proxy_port)

    # Create a MQTT connection from the command line data
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=cmdData.input_endpoint,
        port=cmdData.input_port,
        cert_filepath=cmdData.input_cert,
        pri_key_filepath=cmdData.input_key,
        ca_filepath=cmdData.input_ca,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=cmdData.input_clientId,
        clean_session=False,
        keep_alive_secs=30,
        http_proxy_options=proxy_options,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed)
    
    if not cmdData.input_is_ci:
        print(f"Connecting to {cmdData.input_endpoint} with client ID '{cmdData.input_clientId}'...")
    else:
        print("Connecting to endpoint with client ID")
    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    grpc_server = start_grpc_server()

    rest_thread = threading.Thread(target=start_rest_server, daemon=True)
    rest_thread.start()

    ws_thread = threading.Thread(target=start_websocket_server, daemon=True)
    ws_thread.start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down...", flush=True)
        grpc_server.stop(0)
        rest_thread.join()
        ws_thread.join()

    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")


