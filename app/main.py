import uvicorn
from fastapi import FastAPI, Depends, status as httpStatus, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from . import schemas, models, database, kafka_producer
from .repositories.order_repository import OrderRepository
from .utilities import type_conversion
from decimal import Decimal
from typing import Optional, List
from pydantic import ValidationError


app = FastAPI(
    title='Order Service',
    description='Service to manage customer orders',
    version='1.0.0'
)

@app.on_event('startup')
async def startup_event():
    print('Order Service starting!')
    await database.init_db()
    await kafka_producer.kafka_producer_startup()
    print('Startup completed!')

@app.on_event('shutdown')
async def shutdown_event():
    print('Order Service shutting down!')



def get_order_repo(db: AsyncSession = Depends(database.get_db)) -> OrderRepository:
    return OrderRepository(db)


@app.get('/health', status_code=httpStatus.HTTP_200_OK)
async def health_check():
    return {'status': 'Order Service is healthy'}

@app.post('/orders/', response_model=schemas.Order, status_code=httpStatus.HTTP_201_CREATED)
async def create_order(order: schemas.OrderCreate, db: AsyncSession = Depends(database.get_db)):
    try:

        db_order = models.Order(
            user_id=order.user_id,
            total_amount=order.total_amount,
            status='pending'
        )

        db.add(db_order)
        await db.flush()

        for item_data in order.items:
            db_item = models.OrderItem(
                order_id=db_order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price=item_data.price
            )
            db.add(db_item)
        
        await db.commit()
        
        stmt = select(models.Order).options(joinedload(models.Order.items)).where(models.Order.id==db_order.id) 
        result = await db.execute(stmt)

        order_response = schemas.Order.model_validate(result.scalars().first())

        event_payload = {
            "orderId": str(db_order.id),
            "userId": db_order.user_id,
            "total_amout": float(db_order.total_amount),
            "status": db_order.status,
            "items": [
                {
                    "productId": item.product_id,
                    "quantity": item.quantity,
                    "price": float(item.price)

                } for item in db_order.items
            ], 
            "createdAt": db_order.created_at.isoformat()
        }

        await kafka_producer.send_order_created_message(event_payload)

        return order_response
    except Exception as e:
        await db.rollback()
        print(f'Error creating order: {e}')
        raise HTTPException(
            status_code=httpStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to create order: {e}'
        )

@app.get('/orders/{order_id}', response_model=schemas.Order)
async def get_order(order_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Order).where(models.Order.id == order_id))
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=httpStatus.HTTP_404_NOT_FOUND,
            detail='Order not found'
        )
    
    await db.refresh()
    return order


@app.get('/orders', response_model=schemas.OrdersPaginated)
async def index_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    repo: OrderRepository = Depends(get_order_repo),
    product_id: Optional[List[str]] = Query(None, description='Filter by product_id eg product_id=xyz&product_id=abc'),
    min_amount: Optional[Decimal] = Query(None),
    max_amount: Optional[Decimal] = Query(None),
    status: Optional[str] = Query(None)
):
    try:
        filters = schemas.OrderFilter(
            product_id=product_id,
            min_amount=min_amount,
            max_amount=max_amount,
            status=status
        )
    except ValidationError as e:
        processed_errors = type_conversion.convert_decimal_into_float(e.errors())
        raise HTTPException(
            status_code= httpStatus.HTTP_422_UNPROCESSABLE_ENTITY
        )
    paginated_result = await repo.get_paginated_orders(page=page, page_size=page_size, filters=filters)
    return paginated_result


if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8008, reload=True)