from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.analytics import get_customer_detail, get_customer_orders, get_customer_payments, list_customers

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("")
def customers(
    search: str | None = None,
    country: str | None = None,
    city: str | None = None,
    salesRepEmployeeNumber: int | None = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    return list_customers(
        db,
        search=search,
        country=country,
        city=city,
        sales_rep=salesRepEmployeeNumber,
        limit=limit,
        offset=offset,
    )


@router.get("/{customer_number}")
def customer_detail(customer_number: int, db: Session = Depends(get_db)):
    customer = get_customer_detail(db, customer_number)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/{customer_number}/orders")
def customer_orders(customer_number: int, db: Session = Depends(get_db)):
    return get_customer_orders(db, customer_number)


@router.get("/{customer_number}/payments")
def customer_payments(customer_number: int, db: Session = Depends(get_db)):
    return get_customer_payments(db, customer_number)

