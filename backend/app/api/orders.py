from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.analytics import get_order_detail, list_orders

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
def orders(
    search: str | None = None,
    status: str | None = None,
    customerNumber: int | None = None,
    startDate: str | None = None,
    endDate: str | None = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    return list_orders(
        db,
        search=search,
        status=status,
        customer_number=customerNumber,
        start_date=startDate,
        end_date=endDate,
        limit=limit,
        offset=offset,
    )


@router.get("/{order_number}")
def order_detail(order_number: int, db: Session = Depends(get_db)):
    order = get_order_detail(db, order_number)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

