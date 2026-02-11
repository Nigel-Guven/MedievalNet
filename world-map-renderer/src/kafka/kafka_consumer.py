import json
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from map_renderer import render_world_map
from confluent_kafka import Consumer

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
TOPIC_NAME = "world.generated"

def create_consumer():
    return Consumer({
        "bootstrap.servers": KAFKA_SERVERS,       # internal Docker network
        "group.id": "map-renderer-group",
        "auto.offset.reset": "earliest"
    })
    
def consume():
    consumer = create_consumer()
    print("Connected to brokers:", consumer.list_topics().brokers)
    consumer.subscribe([TOPIC_NAME])
    
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        
        event = json.loads(msg.value())
        world_id = event["worldId"]
        factions = event["factions"]

        render_world_map(world_id, factions)

    consumer.close()
    
def main():
    print("Starting World Map Renderer Microservice...")
    consume()

if __name__ == "__main__":
    main()