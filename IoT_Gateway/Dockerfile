# Usamos la imagen base de Python
FROM python:3.11-slim-bookworm

# Establecemos el directorio de trabajo
WORKDIR /IoT_Gateway

# Instalamos las dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    python3-dev \
    libssl-dev \
    libffi-dev \
    libprotobuf-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Copiamos el archivo requirements.txt y lo usamos para instalar las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Exponemos los puertos necesarios para gRPC, REST y WebSockets
EXPOSE 50051 5000 8080

# Copiamos el código fuente
COPY . .

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sensor.proto

# Comando para ejecutar el IoT Gateway
CMD ["python", "gateway.py"]
