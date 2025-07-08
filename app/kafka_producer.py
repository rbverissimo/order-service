import logging
import json
import os
from aiokafka import AIOKafkaProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('__name__')

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC_ORDER_CREATED = 'order-created'

producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

async def kafka_producer_startup():
    logger.info(f'Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}')
    try:
        await producer.start()
        logger.info('Kafka producer started successfully')
    except Exception as e:
        logger.error(f'Failed to start Kafka ${e}')
        raise

async def kafka_producer_shutdown():
    logger.info('Disconnecting from kafka...')
    try:
        await producer.stop()
        logger.info('Kafka producer disconnected')
    except Exception as e:
        logger.error(f'Unable to disconnect from kafka: {e}')

async def send_order_created_message(order_data: dict):
    try:
        message_value = json.dumps(order_data).encode('utf-8')
        await producer.send_and_wait(TOPIC_ORDER_CREATED, message_value)
        logger.info(f'Message published in {TOPIC_ORDER_CREATED} as {order_data}')
    except Exception as e:
        logger.error(f'Failed to send OrderCreated event for Order ID {order_data.get('id')}: {e} ')

async def get_kafka_producer():
    return producer