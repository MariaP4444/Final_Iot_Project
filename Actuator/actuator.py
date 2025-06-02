# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
import json
from utils.command_line_utils import CommandLineUtils

cmdData = CommandLineUtils.parse_sample_input_pubsub()

received_count = 0
received_all_event = threading.Event()

def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error), flush=True)

def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present), flush=True)

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...", flush=True)
        resubscribe_future, _ = connection.resubscribe_existing_topics()
        resubscribe_future.add_done_callback(on_resubscribe_complete)

def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results), flush=True)
    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))

def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    global received_count
    print("Received message from topic '{}': {}".format(topic, payload), flush=True)
    try:
        data = json.loads(payload.decode())
        print(f"[ALERTA] Nivel de sonido alto: {data['sound_level_db']} dB - {data['timestamp']}", flush=True)
    except Exception as e:
        print("Error al procesar mensaje:", e, flush=True)

    received_count += 1
    if received_count == cmdData.input_count:
        received_all_event.set()

def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print("Connection Successful with return code: {} session present: {}".format(callback_data.return_code, callback_data.session_present), flush=True)

def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    print("Connection failed with error code: {}".format(callback_data.error), flush=True)

def on_connection_closed(connection, callback_data):
    print("Connection closed", flush=True)

if __name__ == '__main__':
    proxy_options = None
    if cmdData.input_proxy_host is not None and cmdData.input_proxy_port != 0:
        proxy_options = http.HttpProxyOptions(
            host_name=cmdData.input_proxy_host,
            port=cmdData.input_proxy_port)

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
        print(f"Connecting to {cmdData.input_endpoint} with client ID '{cmdData.input_clientId}'...", flush=True)
    else:
        print("Connecting to endpoint with client ID", flush=True)

    connect_future = mqtt_connection.connect()
    connect_future.result()
    print("Connected!", flush=True)

    message_count = cmdData.input_count
    message_topic = cmdData.input_topic
    message_string = cmdData.input_message

    topicComplete = "".join([message_topic, "Sede1/Edificio1/Piso1/Area1/Habitacion1/sensorSonido/sensor0/alertaSonidoAlto"])
    print(topicComplete)

    print("Subscribing to topic '{}'...".format(topicComplete), flush=True)
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=topicComplete,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])), flush=True)

    if message_count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...", flush=True)

    received_all_event.wait()
    print("{} message(s) received.".format(received_count), flush=True)

    print("Disconnecting...", flush=True)
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!", flush=True)
