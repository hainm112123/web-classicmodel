from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.analytics import build_pivot, revenue_by_country, revenue_by_product_line, get_top_customers, top_products

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/revenue-by-country")
def report_revenue_by_country(db: Session = Depends(get_db)):
    return revenue_by_country(db)


@router.get("/revenue-by-product-line")
def report_revenue_by_product_line(db: Session = Depends(get_db)):
    return revenue_by_product_line(db)


@router.get("/top-customers")
def report_top_customers(db: Session = Depends(get_db)):
    return get_top_customers(db, limit=10)


@router.get("/top-products")
def report_top_products(db: Session = Depends(get_db)):
    return top_products(db, limit=10)


@router.get("/pivot")
def report_pivot(
    rowDimension: str = "country",
    columnDimension: str = "year",
    metric: str = "sales_revenue",
    db: Session = Depends(get_db),
):
    return build_pivot(db, row_dimension=rowDimension, column_dimension=columnDimension, metric=metric)

