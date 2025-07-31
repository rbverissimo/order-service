import pytest
import random
from unittest.mock import AsyncMock, patch
from app.publishers.kafka_producer import KafkaProducerService
from app.schemas import OrderCreatedEvent, OrderItemEvent
from datetime import datetime

from pytest_asyncio import fixture as async_fixture


@pytest.fixture
def mock_aiokafka_producer(mocker):
    mock_producer = mocker.patch('app.publishers.kafka_producer.AIOKafkaProducer', autospec=True).return_value
    mock_producer.start = AsyncMock()
    mock_producer.stop = AsyncMock()
    mock_producer.send_and_wait = AsyncMock()
    return mock_producer

@async_fixture
async def mock_kafka_producer_service(mock_aiokafka_producer):
    service = KafkaProducerService(bootstrap_servers='mocker_server')
    yield service

@pytest.fixture
def sample_order_created_event():
    return OrderCreatedEvent(
        orderId=str(random.randint(1, 100)),
        userId='user1',
        total_amout=float(1000.0),
        status='pending',
        items=[OrderItemEvent(product_id='productA', quantity=10, price=100.0)],
        createdAt=datetime.now()
    )

@pytest.mark.asyncio
async def test_send_order_created_message(mock_kafka_producer_service, mock_aiokafka_producer, sample_order_created_event):
    await mock_kafka_producer_service.publish_to_order_created_topic(sample_order_created_event)

    mock_aiokafka_producer.send_and_wait.assert_awaited_once()

    call_args = mock_aiokafka_producer.send_and_wait.call_args[0]
    topic = call_args[0]
    message_payload = call_args[1]
    key = call_args[2]

    assert topic == mock_kafka_producer_service.TOPIC_ORDER_CREATED
    assert message_payload.decode('utf-8') == sample_order_created_event.model_dump_json()
    assert key.decode('utf-8') == str(sample_order_created_event.orderId)