import uvicorn
from fastapi import FastAPI, Depends, status

app = FastAPI(
    title='Order Service',
    description='Service to manage customer orders',
    version='1.0.0'
)

@app.on_event('startup')
async def startup_event():
    print('Order Service starting up!')

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8008, reload=True)