import datetime
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, distinct
from .. import schemas, models

class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, order_create: schemas.OrderCreate) -> models.Order | None:
        try:
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
        except Exception as e:
            await self.db.rollback()
            raise e
    
    async def get_order_by_id(self, order_id: int) -> models.Order | None:
        stmt = select(models.Order).options(selectinload(models.Order.items)).where(models.Order.id == order_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_paginated_orders(
            self,
            page: int,
            page_size: int,
            filters: schemas.OrderFilter
    ):
        query = select(models.Order).options(selectinload(models.Order.items))
        conditions = []

        if filters.product_id:
            query = query.join(models.Order.items).where(models.OrderItem.product_id.in_(filters.product_id))
            query = query.distinct(models.Order.id)
        if filters.min_amount is not None:
            conditions.append(models.Order.total_amount >= filters.min_amount)
        if filters.max_amount is not None:
            conditions.append(models.Order.total_amount <= filters.max_amount)
        if filters.status is not None:
            conditions.append(models.Order.status == filters.status)
        
        if conditions:
            query = query.where(and_(*conditions))

        if filters.product_id:
            count_query = select(func.count(distinct(models.Order.id))).select_from(query.subquery())
        else:
            count_query = select(func.count()).select_from(query.subquery())

        total_count = (await self.db.execute(count_query)).scalar_one()
        
        offset = (page - 1) * page_size
        paginated_query = query.offset(offset).limit(page_size)

        result = await self.db.execute(paginated_query)

        orders_orm = []
        for order_obj in result.scalars().unique():
            _ = order_obj.items
            orders_orm.append(order_obj)

        total_pages = (total_count + page_size - 1) // page_size

        return {
            "data": [schemas.Order(id=order.id, user_id=order.user_id, total_amount=order.total_amount, items=order.items, status=order.status, created_at=order.created_at) for order in orders_orm],
            "total_pages" : total_pages,
            "total_count" : total_count,
            "page": page,
            "page_size": page_size 
        }
        

          



