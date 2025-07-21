import uvicorn
from fastapi import FastAPI, status as httpStatus
from . import database, kafka_producer
from app.routers import orders


app = FastAPI(
    title='Order Service',
    description='Service to manage customer orders',
    version='1.0.0'
)

app.include_router(orders.router)

@app.on_event('startup')
async def startup_event():
    print('Order Service starting!')
    await database.init_db()
    await kafka_producer.kafka_producer_startup()
    print('Startup completed!')

@app.on_event('shutdown')
async def shutdown_event():
    print('Order Service shutting down!')


@app.get('/health', status_code=httpStatus.HTTP_200_OK)
async def health_check():
    return {'status': 'Order Service is healthy'}

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8008, reload=True)