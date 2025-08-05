from fastapi import Depends
from ..repositories.order_repository import OrderRepository, get_order_repo
from ..schemas import OrderCreate, Order, OrderCreatedEvent, OrderItemEvent
from app.publishers.kafka_producer import KafkaProducerService, get_kafka_producer_service

from app.database import AsyncSessionLocal

class OrderService:
    def __init__(self, order_repo: OrderRepository, kafka_producer: KafkaProducerService):
        self.order_repo = order_repo
        self.kafka_producer = kafka_producer
    
    async def create_order_and_send_event(self, order_data: OrderCreate):

        try:
            db_order = await self.order_repo.create(order_data)

            async with AsyncSessionLocal() as read_session:
                read_order_repo = get_order_repo(read_session)
                db_order_with_items = await read_order_repo.get_order_by_id(db_order.id)


            if not db_order_with_items:
                raise ValueError('Failed to process order in the database')
            
            print(db_order_with_items.items)
            
            order_created_event = self.__create_order_created_event(db_order_with_items)

            await self.kafka_producer.publish_to_order_created_topic(order_created_event)

            return Order.model_validate(db_order)
        except Exception as e:
            print(f'OrderService: could not process order and publish to topic', e)
            raise e



    def __create_order_created_event(self, db_order: Order) -> OrderCreatedEvent:
        items_for_event = []
        for item in db_order.items:
            items_for_event.append(OrderItemEvent(
                product_id=item.product_id,
                quantity=item.quantity,
                price=float(item.price)
            ))

        return OrderCreatedEvent(
            orderId=str(db_order.id),
            userId=db_order.user_id,
            total_amout=db_order.total_amount,
            status=db_order.status,
            items=items_for_event,
            createdAt=db_order.created_at
        )
    
async def get_order_service(
        order_repo: OrderRepository = Depends(get_order_repo),
        kafka_producer: KafkaProducerService = Depends(get_kafka_producer_service)
    ):
        return OrderService(order_repo, kafka_producer)