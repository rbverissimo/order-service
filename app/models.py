from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchey.sql import func


Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default='pending', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship('Order', back_populates="items")

