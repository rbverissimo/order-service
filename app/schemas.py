
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class OrderItemBase(BaseModel):
    product_id: str
    quantity: int
    price: Decimal

class OrderItemCreateBase(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: str
    total_amount: Decimal
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

class OrderFilter(BaseModel):
    min_amount: Optional[Decimal]
    max_amount: Optional[Decimal]
    status: Optional[str]
    product_id: Optional[List[str]] = Field(None, description='List of products IDs to filter Order considering items that references those IDs')