FROM python:3.11-slim-bookworm

WORKDIR /sensor

COPY requirements.txt .

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sensor.proto

CMD ["python", "client.py"]
