
from pydantic import BaseModel
from datetime import datetime
from typing import List

class OrderItemBase(BaseModel):
    product_id: str
    quantity: int
    price: float

class OrderItemCreateBase(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: str
    total_amount: float
    items: List[OrderItemCreateBase]

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    status: str = 'pending'
    created_at: datetime
    items: List[OrderItem] = []
    class Config:
        from_attributes = True