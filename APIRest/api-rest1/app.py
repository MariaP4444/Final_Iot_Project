from chalice import Chalice, Response
import psycopg2
import os
import json

app = Chalice(app_name='api-rest1')

def get_db_connection():
    conn = psycopg2.connect(
        host="172.31.16.165",
        port="5432",
        database="hospital",
        user="postgres",
        password="0"
    )
    return conn

@app.route('/', methods=['GET'])
def hello():
    return{"hello": "This is the API REST of the hospital1/Sede1/Edificio1/Piso1"}

@app.route('/sensors', methods=['GET'])
def list_sensors():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, tipo, habitacion_id FROM sensor")
        rows = cursor.fetchall()
        sensors = [{'id': r[0], 'nombre': r[1], 'tipo': r[2], 'habitacion_id': r[3]} for r in rows]
        return sensors
    except Exception as e:
        return Response(body={'error': str(e)}, status_code=500)
    finally:
        cursor.close()
        conn.close()

@app.route('/sensors', methods=['POST'])
def create_sensor():
    try:
        request = app.current_request
        data = request.json_body
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sensor (nombre, tipo, habitacion_id) VALUES (%s, %s, %s) RETURNING id",
            (data['nombre'], data['tipo'], data['habitacion_id'])
        )
        sensor_id = cursor.fetchone()[0]
        conn.commit()
        return {'id': sensor_id}
    except Exception as e:
        return Response(body={'error': str(e)}, status_code=500)
    finally:
        cursor.close()
        conn.close()

@app.route('/sensors/{sensor_id}', methods=['GET'])
def get_sensor_events(sensor_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, sensor_id, fecha_hora, datos FROM log_sensor WHERE sensor_id = %s",
            (sensor_id,)
        )
        rows = cursor.fetchall()
        events = [{'id': r[0], 'sensor_id': r[1], 'fecha_hora': r[2].isoformat(), 'datos': r[3]} for r in rows]
        return events
    except Exception as e:
        return Response(body={'error': str(e)}, status_code=500)
    finally:
        cursor.close()
        conn.close()

@app.route('/actuators', methods=['GET'])
def list_actuators():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, tipo, habitacion_id FROM actuador")
        rows = cursor.fetchall()
        actuators = [{'id': r[0], 'nombre': r[1], 'tipo': r[2], 'habitacion_id': r[3]} for r in rows]
        return actuators
    except Exception as e:
        return Response(body={'error': str(e)}, status_code=500)
    finally:
        cursor.close()
        conn.close()

@app.route('/actuators', methods=['POST'])
def create_actuator():
    try:
        request = app.current_request
        data = request.json_body
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO actuador (nombre, tipo, habitacion_id) VALUES (%s, %s, %s) RETURNING id",
            (data['nombre'], data['tipo'], data['habitacion_id'])
        )
        actuator_id = cursor.fetchone()[0]
        conn.commit()
        return {'id': actuator_id}
    except Exception as e:
        return Response(body={'error': str(e)}, status_code=500)
    finally:
        cursor.close()
        conn.close()