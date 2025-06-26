import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://orderuser:orderpassword@order_db:5432/order_db')