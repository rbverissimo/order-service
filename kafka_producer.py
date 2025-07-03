import logging
import os
from aiokafka import AIOKafkaProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('__name__')

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BROKER', 'kafa:9092')

producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

async def kafka_producer_startup():
    logger.info(f'Connecting to Kafka at ${KAFKA_BOOTSTRAP_SERVERS}')
    try:
        await producer.start()
        logger.info('Kafka producer started successfully')
    except Exception as e:
        logger.error(f'Failed to start Kafka ${e}')
        raise
