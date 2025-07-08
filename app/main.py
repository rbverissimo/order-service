import uvicorn
from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from . import schemas, models, database, kafka_producer

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


@app.get('/health', status_code=status.HTTP_200_OK)
async def health_check():
    return {'status': 'Order Service is healthy'}

@app.post('/orders/', response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
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

        await kafka_producer.send_order_created_message(order_response.model_dump())

        return order_response
    except Exception as e:
        await db.rollback()
        print(f'Error creating order: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to create order: {e}'
        )

@app.get('/orders/{order_id}', response_model=schemas.Order)
async def get_order(order_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Order).where(models.Order.id == order_id))
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order not found'
        )
    
    await db.refresh()
    return order



if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8008, reload=True)