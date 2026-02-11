FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .
COPY templates ./templates

CMD ["python", "kafka/kafka_consumer.py"]
