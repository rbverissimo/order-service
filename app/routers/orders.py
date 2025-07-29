from fastapi import APIRouter, status as httpStatus, Depends, HTTPException, Query
from pydantic import ValidationError
from typing import Optional, List
from decimal import Decimal
from ..repositories.order_repository import OrderRepository, get_order_repo
from ..utilities import type_conversion
from .. import schemas, kafka_producer

router = APIRouter(prefix='/orders', tags=['Orders'])


@router.post('', response_model=schemas.Order, status_code=httpStatus.HTTP_201_CREATED)
async def create_order(order: schemas.OrderCreate, repo: OrderRepository = Depends(get_order_repo)):
    try:

        db_order = await repo.create(order)

        if not db_order:
            raise HTTPException(
                status_code=httpStatus.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to create order due to an unknown server state'
            )

        order_response = schemas.Order.model_validate(db_order)

        event_payload = {
            "orderId": str(db_order.id),
            "userId": db_order.user_id,
            "total_amount": float(db_order.total_amount),
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
        print(f'Error creating order: {e}')
        raise HTTPException(
            status_code=httpStatus.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to create order: {e}'
        )

@router.get('/{order_id}', response_model=schemas.Order)
async def get_order(order_id: int, repo: OrderRepository = Depends(get_order_repo)):
    
    order = await repo.get_order_by_id(order_id)

    print(order)
    
    if not order:
        raise HTTPException(
            status_code=httpStatus.HTTP_404_NOT_FOUND,
            detail='Order not found'
        )
    
    return order


@router.get('', response_model=schemas.OrdersPaginated)
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
        processed_errors = type_conversion.convert_decimal_into_serializable_str(e.errors())
        raise HTTPException(
            status_code= httpStatus.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=processed_errors
        )
    paginated_result = await repo.get_paginated_orders(page=page, page_size=page_size, filters=filters)
    return paginated_result
