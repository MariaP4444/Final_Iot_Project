FROM python:3.11-slim-bookworm

WORKDIR /SensorWS

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "client.py"]

