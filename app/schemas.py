
from pydantic import BaseModel, Field, ConfigDict, model_validator
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
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

class OrderFilter(BaseModel):
    min_amount: Optional[Decimal]
    max_amount: Optional[Decimal]
    status: Optional[str]
    product_id: Optional[List[str]] = Field(None, description='List of products IDs to filter Order considering items that references those IDs')

    @model_validator(mode='after')
    def validate_min_max_amount(self) -> 'OrderFilter':
        if self.min_amount is not None and self.max_amount is not None:
            if self.min_amount > self.max_amount:
                raise ValueError('min_amount should be lower than max_amount parameter')
        return self
    

class OrdersPaginated(BaseModel):
    total_count: int
    page: int
    page_size: int
    total_pages: int
    data: List[Order]

class OrderItemEvent(OrderItemBase):
    pass

class OrderCreatedEvent(BaseModel):
    orderId: str
    userId: str
    total_amout: float
    status: str
    items: List[OrderItemEvent]
    createdAt: datetime

    model_config=ConfigDict(from_attributes=True, populate_by_name=True)