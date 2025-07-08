import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import schemas, models

class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, order_create: schemas.OrderCreate) -> models.Order | None:
        db_order = models.Order(
            user_id=order_create.user_id,
            total_amount=order_create.total_amount,
            status='pending',
            created_at=datetime.datetime.now(datetime.timezone.utc)
        )

        self.db.add(db_order)
        await self.db.flush()

        for item_data in order_create.items:
            db_item = models.OrderItem(
                order_id=db_order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price=item_data.price
            )
            self.db.add(db_item)

        await self.db.commit()

        stmt = select(models.Order).options(joinedload(models.Order.items)).where(models.Order.id==db_order.id) 
        result = await self.db.execute(stmt)
        return result.scalars().first()

