from fastapi import Depends
from ..repositories.order_repository import OrderRepository, get_order_repo
from ..schemas import OrderCreate, Order, OrderCreatedEvent, OrderItemEvent
from .. import kafka_producer

class OrderService:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo
    
    async def create_order_and_send_event(self, order_data: OrderCreate):
        db_order = self.order_repo.create(order_data)

        if not db_order:
            raise ValueError('Failed to process order in the database')
        
        order_created_event = self.create_order_and_send_event(db_order)

        await kafka_producer.send_order_created_message(order_created_event)

        return Order.model_validate(db_order)



    def create_order_created_event(self, db_order: Order) -> OrderCreatedEvent:
        items_for_event = []
        for item in db_order.items:
            items_for_event.append(OrderItemEvent(
                product_id=item.product_id,
                quantity=item.quantity,
                price=float(item.price)
            ))

        return OrderCreatedEvent(
            orderId=db_order.id,
            userId=db_order.user_id,
            total_amout=db_order.total_amount,
            status=db_order.status,
            items=items_for_event,
            createdAt=db_order.created_at
        )
    
async def get_order_service(
        order_repo: OrderRepository = Depends(get_order_repo)
    ):
        return OrderService(order_repo)