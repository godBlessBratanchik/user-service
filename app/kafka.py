import os
import json
import asyncio
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "false").lower() == "true"

TOPIC_USERS_REGISTERED = os.getenv("TOPIC_USERS_REGISTERED", "users.registered")
TOPIC_PROFILE_EVENTS = os.getenv("TOPIC_PROFILE_EVENTS", "profile.events")

class KafkaProducerManager:
    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None
        self.enabled = KAFKA_ENABLED

    async def start(self):
        if not self.enabled:
            print("⊘ Kafka producer disabled")
            return
        self.producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()
        print(f"✓ Kafka producer started: {KAFKA_BOOTSTRAP}")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            print("✓ Kafka producer stopped")

    async def send_event(self, topic: str, event: Dict[str, Any]):
        if not self.enabled:
            print(f"⊘ Kafka disabled, event not sent: {event.get('event_type', 'unknown')}")
            return
        if not self.producer:
            raise RuntimeError("Kafka producer not started")
        try:
            await self.producer.send_and_wait(topic, value=event)
            print(f"→ Event sent to {topic}: {event.get('event_type', 'unknown')}")
        except KafkaError as e:
            print(f"✗ Failed to send event to {topic}: {e}")
            raise

kafka_producer = KafkaProducerManager()

async def get_kafka_producer() -> KafkaProducerManager:
    return kafka_producer

class KafkaConsumerManager:
    def __init__(self, topic: str, group_id: str):
        self.topic = topic
        self.group_id = group_id
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.enabled = KAFKA_ENABLED

    async def start(self):
        if not self.enabled:
            print(f"⊘ Kafka consumer disabled: topic={self.topic}")
            return
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        await self.consumer.start()
        print(f"✓ Kafka consumer started: topic={self.topic}, group={self.group_id}")

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
            print(f"✓ Kafka consumer stopped: {self.topic}")
