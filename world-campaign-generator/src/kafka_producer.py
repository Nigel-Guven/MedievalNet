from confluent_kafka import Producer
import json
import socket

def create_producer():
    conf = {
        "bootstrap.servers": "localhost:9092",  # Kafka broker
        "client.id": socket.gethostname(),
        "acks": "all",            # ensures durability
        "retries": 5,
    }
    return Producer(conf)

def send_world_event(world_event, key):
    producer = create_producer()
    producer.produce(
        topic="world.generated",
        key=key,
        value=json.dumps(world_event, default=str).encode("utf-8")
    )
    producer.flush()  # ensures message is sent before exiting

def faction_to_dictionary(faction):
    return {
        "faction_name": faction.faction_name,
        "ai_model": faction.ai_model.value if hasattr(faction.ai_model, "value") else str(faction.ai_model),
        "ai_label": faction.ai_label,
        "denari": faction.denari,
        "kings_purse": faction.kings_purse,
        "settlements": [
            {
                "province_name": s.province_name,
                "settlement_name": s.settlement_name,
                "culture": s.culture,
                "rebels_type": s.rebels_type,
                "rgb_value": list(s.rgb_value),  # convert tuple to list
                "features": s.features,
                "famine_level": s.famine_level,
                "agriculture_level": s.agriculture_level,
                "religions": s.religions,
                "settlement_positionX": s.settlement_positionX,
                "settlement_positionY": s.settlement_positionY,
                "settlement_level": getattr(s.settlement_configuration, "level", None),
                "population": getattr(s.settlement_configuration, "population", None),
                "is_castle": getattr(s.settlement_configuration, "is_castle", None),
                "buildings": [str(b) for b in getattr(s.settlement_configuration, "buildings", [])]
            }
            for s in faction.settlements
        ],
        "factionRelations": {str(k): v for k, v in faction.factionRelations.items()},  # convert Decimal keys to string
        "enemies": faction.enemies
    }