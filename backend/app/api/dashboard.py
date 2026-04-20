from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.analytics import (
    get_dashboard_summary,
    get_monthly_payments,
    get_monthly_sales,
    get_recent_orders,
    get_top_customers,
    get_top_product_lines,
    orders_by_status,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)


@router.get("/monthly-sales")
def monthly_sales(db: Session = Depends(get_db)):
    return get_monthly_sales(db)


@router.get("/monthly-payments")
def monthly_payments(db: Session = Depends(get_db)):
    return get_monthly_payments(db)


@router.get("/recent-orders")
def recent_orders(db: Session = Depends(get_db)):
    return get_recent_orders(db)


@router.get("/top-customers")
def top_customers(db: Session = Depends(get_db)):
    return get_top_customers(db)


@router.get("/top-product-lines")
def top_product_lines(db: Session = Depends(get_db)):
    return get_top_product_lines(db)


@router.get("/orders-by-status")
def order_status_breakdown(db: Session = Depends(get_db)):
    return orders_by_status(db)

