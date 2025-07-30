import pytest
import random
from unittest.mock import MagicMock, AsyncMock
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService
from app.publishers.kafka_producer import KafkaProducerService
from app.models import Order as DBOrder
from app.schemas import OrderCreatedEvent, OrderCreate, OrderItemEvent

from datetime import datetime

@pytest.fixture
def mock_order_repo(mocker):
    mock = mocker.MagicMock(spec=OrderRepository)
    mock.create = AsyncMock()
    return mock

@pytest.fixture
def mock_kafka_producer(mocker):
    mock = mocker.MagicMock(spec=KafkaProducerService)
    mock.publish_to_order_created_topic = AsyncMock()
    return mock


@pytest.fixture
def orders_service(mock_order_repo, mock_kafka_producer):
    return OrderService(mock_order_repo, mock_kafka_producer)

@pytest.fixture
def sample_order_create():
    return OrderCreate(
        user_id='user1',
        total_amount=1000.0,
        items=[
            {'product_id': 'productA', 'quantity': 1, 'price' : 1000.0}
        ]
    )

@pytest.fixture
def mock_db_order(sample_order_create):
    mock_order = MagicMock(spec=DBOrder)
    mock_order.id = random.randint(1, 100)
    mock_order.user_id = sample_order_create.user_id
    mock_order.total_amount = sample_order_create.total_amount
    mock_order.status = 'pending'
    mock_order.created_at = datetime.now()

    mock_order.items = [
        MagicMock(
            product_id=item_data.product_id, 
            quantity=item_data.quantity,
            price=item_data.price
        ) for item_data in sample_order_create.items
    ] 

    return mock_order

@pytest.mark.asyncio
async def test_create_order_success(
    orders_service,
    mock_order_repo,
    mock_kafka_producer,
    sample_order_create,
    mock_db_order
): 
    mock_order_repo.create.return_value = mock_db_order
    returned_order = await orders_service.create_order_and_send_event(sample_order_create)

    mock_order_repo.create.assert_awaited_once_with(sample_order_create)

    expected_event_items = [
        OrderItemEvent(
            product_id=item.product_id,
            quantity=item.quantity,
            price=float(item.price)
        ) for item in mock_db_order.items
    ]
    
    expected_order_created_event = OrderCreatedEvent(
        orderId=str(mock_db_order.id),
        userId=mock_db_order.user_id,
        total_amout=mock_db_order.total_amount,
        status=mock_db_order.status,
        items= expected_event_items,
        createdAt=mock_db_order.created_at
    )

    mock_kafka_producer.publish_to_order_created_topic.assert_awaited_once_with(expected_order_created_event)

    assert returned_order.id == mock_db_order.id
    assert returned_order.user_id == mock_db_order.user_id
    assert returned_order.total_amount == float(mock_db_order.total_amount)
    assert returned_order.status == mock_db_order.status
    assert len(returned_order.items) == len(mock_db_order.items)