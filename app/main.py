import uvicorn
from fastapi import FastAPI, Depends, status
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
    pass


if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8008, reload=True)