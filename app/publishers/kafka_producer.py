from aiokafka import AIOKafkaProducer
from app.core.config import Settings
from app.schemas import OrderCreatedEvent
from typing import AsyncGenerator


class KafkaProducerService:

    TOPIC_ORDER_CREATED = 'order-created'

    def __init__(self, bootstrap_servers: str):
        self.producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)

    async def start(self):
        await self.producer.start()
        print('Kafka producer started!')
    
    async def stop(self):
        await self.producer.stop()
        print('Kafka producer stopped!')
    
    async def publish_to_order_created_topic(self, event: OrderCreatedEvent):
        try:
            topic = self.TOPIC_ORDER_CREATED
            message_payload = event.model_dump_json().encode('utf-8')
            key=str(event.orderId).encode('utf-8')
            await self.producer.send_and_wait(topic, message_payload, key) 
        except Exception as e:
            print(f'Failed to sent message to topic {topic}: {message_payload}')
            raise e

async def get_kafka_producer_service() -> AsyncGenerator[KafkaProducerService, None]:
    producer_service = KafkaProducerService(bootstrap_servers=Settings.KAFKA_BOOTSTRAP_SERVERS)
    try:
        await producer_service.start()
        yield producer_service
    finally:
        await producer_service.stop()