-- Tabla Piso
CREATE TABLE piso (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla Área (sin claves foráneas aún)
CREATE TABLE area (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    piso_id INT NOT NULL
);

-- Tabla Habitación
CREATE TABLE habitacion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    area_id INT NOT NULL
);

-- Tabla Sensor
CREATE TABLE sensor (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    habitacion_id INT NOT NULL
);

-- Tabla Actuador
CREATE TABLE actuador (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    habitacion_id INT NOT NULL
);

-- Tabla Log de Sensor
CREATE TABLE log_sensor (
    id SERIAL PRIMARY KEY,
    sensor_id INT NOT NULL,
    fecha_hora TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    datos JSONB NOT NULL
);

-- ========================
-- Relación entre tablas
-- ========================

-- area.piso_id → piso.id
ALTER TABLE area
ADD CONSTRAINT fk_area_piso
FOREIGN KEY (piso_id) REFERENCES piso(id)
ON DELETE CASCADE;

-- habitacion.area_id → area.id
ALTER TABLE habitacion
ADD CONSTRAINT fk_habitacion_area
FOREIGN KEY (area_id) REFERENCES area(id)
ON DELETE CASCADE;

-- sensor.habitacion_id → habitacion.id
ALTER TABLE sensor
ADD CONSTRAINT fk_sensor_habitacion
FOREIGN KEY (habitacion_id) REFERENCES habitacion(id)
ON DELETE CASCADE;

-- actuador.habitacion_id → habitacion.id
ALTER TABLE actuador
ADD CONSTRAINT fk_actuador_habitacion
FOREIGN KEY (habitacion_id) REFERENCES habitacion(id)
ON DELETE CASCADE;

-- log_sensor.sensor_id → sensor.id
ALTER TABLE log_sensor
ADD CONSTRAINT fk_logsensor_sensor
FOREIGN KEY (sensor_id) REFERENCES sensor(id)
ON DELETE CASCADE;


-- Insertar un piso de ejemplo
INSERT INTO piso (nombre) VALUES ('Piso 1') RETURNING id;

-- Supongamos que el id del piso insertado es 1
-- Insertar un área conectada al piso
INSERT INTO area (nombre, piso_id) VALUES ('Área A', 1) RETURNING id;

-- Supongamos que el id del área es 1
-- Insertar una habitación en esa área
INSERT INTO habitacion (nombre, area_id) VALUES ('Habitación 101', 1) RETURNING id;

-- Supongamos que el id de la habitación es 1
-- Insertar Sensor de Movimiento
INSERT INTO sensor (id, nombre, tipo, habitacion_id) 
VALUES (3, 'Sensor Movimiento 1', 'movimiento', 1) RETURNING id;

-- Insertar Sensor de Sonido
INSERT INTO sensor (id, nombre, tipo, habitacion_id) 
VALUES (2, 'Sensor Sonido 1', 'sonido', 1) RETURNING id;

-- Insertar Actuador en la misma habitación
INSERT INTO actuador (nombre, tipo, habitacion_id) 
VALUES ('Actuador Ventilador 1', 'ventilador', 1);