
from pydantic import BaseModel, Field, ConfigDict
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

class OrdersPaginated(BaseModel):
    total_count: int
    page: int
    page_size: int
    total_pages: int
    data: List[Order]

try:
    dummy_data = {
        "id": 1,
        "user_id": "user123",
        "total_amount": "100.00",
        "status": "completed",
        "created_at": datetime.now(),
        "items": [
            {"id": 101, "order_id": 1, "product_id": "product_A", "quantity": 1, "price": "50.00"},
            {"id": 102, "order_id": 1, "product_id": "product_B", "quantity": 2, "price": "25.00"}
        ]
    }

    class MockOrderItem:
        def __init__(self, data):
            for k, v in data.items():
                setattr(self, k, v)
    
    class MockOrder:
        def __init__(self, data):
            for k, v in data.items():
                if k == 'items':
                    self.items = [MockOrderItem(item_data) for item_data in v]
                else:
                    setattr(self, k, v)

    mock_order_orm = MockOrder(dummy_data)
    validated_order = Order(id=mock_order_orm.id, user_id=mock_order_orm.user_id, total_amount=mock_order_orm.total_amount, items=mock_order_orm.items, status=mock_order_orm.status, created_at=mock_order_orm.created_at)
    print('Test passed successfully!')

except AttributeError as e:
    print(f'AttributeError caught during test {e}')
except Exception as e:
    print(f'Error found during testing: {e}')   