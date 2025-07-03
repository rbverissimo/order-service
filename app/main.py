import uvicorn
from fastapi import FastAPI, Depends, status
from contextlib import asynccontextmanager

async def lifespan(app: FastAPI):
    print('Order Service is running!')
    yield
    print('Order Service has been shutdown!')

app = FastAPI(
    title='Order Service',
    description='Service to manage customer orders',
    version='1.0.0',
    lifespan=lifespan
)

@app.get('/health', status_code=status.HTTP_200_OK)
async def health_check():
    return {'status': 'Order Service is healthy'}

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8008, reload=True)