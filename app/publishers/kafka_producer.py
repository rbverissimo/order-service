from aiokafka import AIOKafkaProducer
from ..core.config import Settings
from app.schemas import OrderCreatedEvent


class KafkaProducerService:
    def __init__(self, bootstrap_servers: str):
        self.producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)

    async def start(self):
        await self.producer.start()
        print('Kafka producer started!')
    
    async def stop(self):
        await self.producer.stop()
        print('Kafka producer stopped!')
    
    async def publish_to_order_created_topic(self, event: OrderCreatedEvent):
        pass

kafka_producer_service: KafkaProducerService = None

async def get_kafka_producer_service() -> KafkaProducerService:
    global kafka_producer_service
    if kafka_producer_service is None:
        kafka_producer_service = KafkaProducerService(bootstrap_servers=Settings.KAFKA_BOOTSTRAP_SERVERS)
    return kafka_producer_service