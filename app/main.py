import uvicorn
from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import schemas, models, database, kafka_producer

app = FastAPI(
    title='Order Service',
    description='Service to manage customer orders',
    version='1.0.0'
)

@app.on_event('startup')
async def startup_event():
    print('Order Service starting!')

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
        await db.refresh(db_order)

        order_response = schemas.Order.model_validate(db_order)

        await kafka_producer.send_order_created_message(order_response.model_dump())

        return order_response
    except Exception as e:
        db.rollback()
        print(f'Error creating order: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to create order: {e}'
        )

    



if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8008, reload=True)