from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from sqlalchemy import String, and_, cast, distinct, extract, func, literal, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Customer, Employee, Order, OrderDetail, Payment, Product, ProductLine


def as_float(value: Decimal | None) -> float:
    return float(value or 0)


def order_total_expression():
    return OrderDetail.quantityOrdered * OrderDetail.priceEach


def customer_filters(
    search: str | None = None,
    country: str | None = None,
    city: str | None = None,
    sales_rep: int | None = None,
):
    filters = []
    if search:
        like_term = f"%{search}%"
        filters.append(
            or_(
                Customer.customerName.ilike(like_term),
                Customer.contactFirstName.ilike(like_term),
                Customer.contactLastName.ilike(like_term),
                cast(Customer.customerNumber, String).ilike(like_term),
            )
        )
    if country:
        filters.append(Customer.country == country)
    if city:
        filters.append(Customer.city == city)
    if sales_rep:
        filters.append(Customer.salesRepEmployeeNumber == sales_rep)
    return filters


def get_dashboard_summary(db: Session) -> dict:
    order_total = func.sum(order_total_expression())

    customer_count = db.scalar(select(func.count(Customer.customerNumber))) or 0
    order_count = db.scalar(select(func.count(Order.orderNumber))) or 0
    total_sales = db.scalar(select(order_total).select_from(OrderDetail)) or 0
    total_payments = db.scalar(select(func.sum(Payment.amount)).select_from(Payment)) or 0
    order_totals = (
        select(OrderDetail.orderNumber.label("orderNumber"), func.sum(order_total_expression()).label("total"))
        .group_by(OrderDetail.orderNumber)
        .subquery()
    )
    average_order_value = db.scalar(select(func.coalesce(func.avg(order_totals.c.total), 0)).select_from(order_totals)) or 0

    return {
        "customers": customer_count,
        "orders": order_count,
        "salesRevenue": as_float(total_sales),
        "paymentsReceived": as_float(total_payments),
        "averageOrderValue": as_float(average_order_value),
    }


def get_monthly_sales(db: Session) -> list[dict]:
    stmt = (
        select(
            extract("year", Order.orderDate).label("year"),
            extract("month", Order.orderDate).label("month"),
            func.sum(order_total_expression()).label("value"),
        )
        .join(OrderDetail, Order.orderNumber == OrderDetail.orderNumber)
        .group_by("year", "month")
        .order_by("year", "month")
    )
    rows = db.execute(stmt).all()
    return [
        {"period": f"{int(row.year):04d}-{int(row.month):02d}", "value": as_float(row.value)}
        for row in rows
    ]


def get_monthly_payments(db: Session) -> list[dict]:
    stmt = (
        select(
            extract("year", Payment.paymentDate).label("year"),
            extract("month", Payment.paymentDate).label("month"),
            func.sum(Payment.amount).label("value"),
        )
        .group_by("year", "month")
        .order_by("year", "month")
    )
    rows = db.execute(stmt).all()
    return [
        {"period": f"{int(row.year):04d}-{int(row.month):02d}", "value": as_float(row.value)}
        for row in rows
    ]


def get_recent_orders(db: Session, limit: int = 10) -> list[dict]:
    totals_subquery = (
        select(OrderDetail.orderNumber, func.sum(order_total_expression()).label("total"))
        .group_by(OrderDetail.orderNumber)
        .subquery()
    )
    stmt = (
        select(
            Order.orderNumber,
            Order.orderDate,
            Order.status,
            Customer.customerName,
            totals_subquery.c.total,
        )
        .join(Customer, Customer.customerNumber == Order.customerNumber)
        .join(totals_subquery, totals_subquery.c.orderNumber == Order.orderNumber)
        .order_by(Order.orderDate.desc(), Order.orderNumber.desc())
        .limit(limit)
    )
    return [
        {
            "orderNumber": row.orderNumber,
            "orderDate": row.orderDate.isoformat(),
            "status": row.status,
            "customerName": row.customerName,
            "total": as_float(row.total),
        }
        for row in db.execute(stmt).all()
    ]


def get_top_customers(db: Session, limit: int = 5) -> list[dict]:
    stmt = (
        select(
            Customer.customerNumber,
            Customer.customerName,
            func.sum(order_total_expression()).label("value"),
        )
        .join(Order, Order.customerNumber == Customer.customerNumber)
        .join(OrderDetail, OrderDetail.orderNumber == Order.orderNumber)
        .group_by(Customer.customerNumber, Customer.customerName)
        .order_by(func.sum(order_total_expression()).desc())
        .limit(limit)
    )
    return [
        {
            "customerNumber": row.customerNumber,
            "customerName": row.customerName,
            "value": as_float(row.value),
        }
        for row in db.execute(stmt).all()
    ]


def get_top_product_lines(db: Session, limit: int = 5) -> list[dict]:
    stmt = (
        select(ProductLine.productLine, func.sum(order_total_expression()).label("value"))
        .join(Product, Product.productLine == ProductLine.productLine)
        .join(OrderDetail, OrderDetail.productCode == Product.productCode)
        .group_by(ProductLine.productLine)
        .order_by(func.sum(order_total_expression()).desc())
        .limit(limit)
    )
    return [
        {"label": row.productLine, "value": as_float(row.value)}
        for row in db.execute(stmt).all()
    ]


def list_customers(
    db: Session,
    *,
    search: str | None,
    country: str | None,
    city: str | None,
    sales_rep: int | None,
    limit: int,
    offset: int,
) -> dict:
    totals_subquery = (
        select(
            Order.customerNumber.label("customerNumber"),
            func.sum(order_total_expression()).label("salesRevenue"),
            func.count(distinct(Order.orderNumber)).label("orderCount"),
        )
        .join(OrderDetail, OrderDetail.orderNumber == Order.orderNumber)
        .group_by(Order.customerNumber)
        .subquery()
    )
    payment_subquery = (
        select(
            Payment.customerNumber.label("customerNumber"),
            func.sum(Payment.amount).label("paymentsReceived"),
        )
        .group_by(Payment.customerNumber)
        .subquery()
    )

    filters = customer_filters(search, country, city, sales_rep)
    base_stmt = (
        select(
            Customer.customerNumber,
            Customer.customerName,
            Customer.country,
            Customer.city,
            Customer.creditLimit,
            Customer.salesRepEmployeeNumber,
            Employee.firstName,
            Employee.lastName,
            func.coalesce(totals_subquery.c.orderCount, 0).label("orderCount"),
            func.coalesce(totals_subquery.c.salesRevenue, 0).label("salesRevenue"),
            func.coalesce(payment_subquery.c.paymentsReceived, 0).label("paymentsReceived"),
        )
        .outerjoin(Employee, Employee.employeeNumber == Customer.salesRepEmployeeNumber)
        .outerjoin(totals_subquery, totals_subquery.c.customerNumber == Customer.customerNumber)
        .outerjoin(payment_subquery, payment_subquery.c.customerNumber == Customer.customerNumber)
        .where(and_(*filters) if filters else literal(True))
    )

    total = db.scalar(select(func.count()).select_from(base_stmt.subquery())) or 0
    rows = db.execute(
        base_stmt.order_by(Customer.customerName).limit(limit).offset(offset)
    ).all()

    items = []
    for row in rows:
        sales_rep_name = None
        if row.firstName and row.lastName:
            sales_rep_name = f"{row.firstName} {row.lastName}"
        items.append(
            {
                "customerNumber": row.customerNumber,
                "customerName": row.customerName,
                "country": row.country,
                "city": row.city,
                "creditLimit": as_float(row.creditLimit),
                "salesRepEmployeeNumber": row.salesRepEmployeeNumber,
                "salesRepName": sales_rep_name,
                "orderCount": row.orderCount,
                "salesRevenue": as_float(row.salesRevenue),
                "paymentsReceived": as_float(row.paymentsReceived),
            }
        )
    return {"total": total, "items": items}


def get_customer_detail(db: Session, customer_number: int) -> dict | None:
    customer = db.get(Customer, customer_number)
    if customer is None:
        return None

    sales_total = db.scalar(
        select(func.sum(order_total_expression()))
        .select_from(Order)
        .join(OrderDetail, OrderDetail.orderNumber == Order.orderNumber)
        .where(Order.customerNumber == customer_number)
    ) or 0
    payments_total = db.scalar(
        select(func.sum(Payment.amount)).where(Payment.customerNumber == customer_number)
    ) or 0
    order_count = db.scalar(
        select(func.count(Order.orderNumber)).where(Order.customerNumber == customer_number)
    ) or 0

    sales_rep_name = None
    if customer.salesRep:
        sales_rep_name = f"{customer.salesRep.firstName} {customer.salesRep.lastName}"

    return {
        "customerNumber": customer.customerNumber,
        "customerName": customer.customerName,
        "contactName": f"{customer.contactFirstName} {customer.contactLastName}",
        "phone": customer.phone,
        "country": customer.country,
        "city": customer.city,
        "state": customer.state,
        "creditLimit": as_float(customer.creditLimit),
        "salesRepName": sales_rep_name,
        "orderCount": order_count,
        "salesRevenue": as_float(sales_total),
        "paymentsReceived": as_float(payments_total),
        "outstandingBalance": as_float(sales_total - payments_total),
    }


def get_customer_orders(db: Session, customer_number: int) -> list[dict]:
    stmt = (
        select(
            Order.orderNumber,
            Order.orderDate,
            Order.status,
            func.sum(order_total_expression()).label("total"),
        )
        .join(OrderDetail, OrderDetail.orderNumber == Order.orderNumber)
        .where(Order.customerNumber == customer_number)
        .group_by(Order.orderNumber, Order.orderDate, Order.status)
        .order_by(Order.orderDate.desc(), Order.orderNumber.desc())
    )
    return [
        {
            "orderNumber": row.orderNumber,
            "orderDate": row.orderDate.isoformat(),
            "status": row.status,
            "total": as_float(row.total),
        }
        for row in db.execute(stmt).all()
    ]


def get_customer_payments(db: Session, customer_number: int) -> list[dict]:
    stmt = (
        select(Payment.checkNumber, Payment.paymentDate, Payment.amount)
        .where(Payment.customerNumber == customer_number)
        .order_by(Payment.paymentDate.desc(), Payment.checkNumber.desc())
    )
    return [
        {
            "checkNumber": row.checkNumber,
            "paymentDate": row.paymentDate.isoformat(),
            "amount": as_float(row.amount),
        }
        for row in db.execute(stmt).all()
    ]


def list_orders(
    db: Session,
    *,
    search: str | None,
    status: str | None,
    customer_number: int | None,
    start_date: str | None,
    end_date: str | None,
    limit: int,
    offset: int,
) -> dict:
    filters = []
    if search:
        like_term = f"%{search}%"
        filters.append(
            or_(
                Customer.customerName.ilike(like_term),
                cast(Order.orderNumber, String).ilike(like_term),
            )
        )
    if status:
        filters.append(Order.status == status)
    if customer_number:
        filters.append(Order.customerNumber == customer_number)
    if start_date:
        filters.append(Order.orderDate >= start_date)
    if end_date:
        filters.append(Order.orderDate <= end_date)

    stmt = (
        select(
            Order.orderNumber,
            Order.orderDate,
            Order.requiredDate,
            Order.shippedDate,
            Order.status,
            Customer.customerNumber,
            Customer.customerName,
            func.sum(order_total_expression()).label("total"),
        )
        .join(Customer, Customer.customerNumber == Order.customerNumber)
        .join(OrderDetail, OrderDetail.orderNumber == Order.orderNumber)
        .where(and_(*filters) if filters else literal(True))
        .group_by(
            Order.orderNumber,
            Order.orderDate,
            Order.requiredDate,
            Order.shippedDate,
            Order.status,
            Customer.customerNumber,
            Customer.customerName,
        )
    )
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.execute(stmt.order_by(Order.orderDate.desc(), Order.orderNumber.desc()).limit(limit).offset(offset)).all()
    items = [
        {
            "orderNumber": row.orderNumber,
            "orderDate": row.orderDate.isoformat(),
            "requiredDate": row.requiredDate.isoformat(),
            "shippedDate": row.shippedDate.isoformat() if row.shippedDate else None,
            "status": row.status,
            "customerNumber": row.customerNumber,
            "customerName": row.customerName,
            "total": as_float(row.total),
        }
        for row in rows
    ]
    return {"total": total, "items": items}


def get_order_detail(db: Session, order_number: int) -> dict | None:
    order = db.execute(
        select(Order)
        .options(joinedload(Order.customer), joinedload(Order.details).joinedload(OrderDetail.product))
        .where(Order.orderNumber == order_number)
    ).unique().scalar_one_or_none()
    if order is None:
        return None

    lines = []
    total = Decimal("0")
    for detail in sorted(order.details, key=lambda item: item.orderLineNumber):
        line_total = detail.priceEach * detail.quantityOrdered
        total += line_total
        lines.append(
            {
                "orderLineNumber": detail.orderLineNumber,
                "productCode": detail.productCode,
                "productName": detail.product.productName,
                "productLine": detail.product.productLine,
                "quantityOrdered": detail.quantityOrdered,
                "priceEach": as_float(detail.priceEach),
                "lineTotal": as_float(line_total),
            }
        )

    return {
        "orderNumber": order.orderNumber,
        "orderDate": order.orderDate.isoformat(),
        "requiredDate": order.requiredDate.isoformat(),
        "shippedDate": order.shippedDate.isoformat() if order.shippedDate else None,
        "status": order.status,
        "comments": order.comments,
        "customer": {
            "customerNumber": order.customer.customerNumber,
            "customerName": order.customer.customerName,
        },
        "total": as_float(total),
        "lines": lines,
    }


def revenue_by_country(db: Session) -> list[dict]:
    stmt = (
        select(Customer.country.label("label"), func.sum(order_total_expression()).label("value"))
        .join(Order, Order.customerNumber == Customer.customerNumber)
        .join(OrderDetail, OrderDetail.orderNumber == Order.orderNumber)
        .group_by(Customer.country)
        .order_by(func.sum(order_total_expression()).desc())
    )
    return [{"label": row.label, "value": as_float(row.value)} for row in db.execute(stmt).all()]


def revenue_by_product_line(db: Session) -> list[dict]:
    stmt = (
        select(Product.productLine.label("label"), func.sum(order_total_expression()).label("value"))
        .join(OrderDetail, OrderDetail.productCode == Product.productCode)
        .group_by(Product.productLine)
        .order_by(func.sum(order_total_expression()).desc())
    )
    return [{"label": row.label, "value": as_float(row.value)} for row in db.execute(stmt).all()]


def top_products(db: Session, limit: int = 10) -> list[dict]:
    stmt = (
        select(
            Product.productCode,
            Product.productName,
            Product.productLine,
            func.sum(OrderDetail.quantityOrdered).label("quantity"),
            func.sum(order_total_expression()).label("value"),
        )
        .join(OrderDetail, OrderDetail.productCode == Product.productCode)
        .group_by(Product.productCode, Product.productName, Product.productLine)
        .order_by(func.sum(order_total_expression()).desc())
        .limit(limit)
    )
    return [
        {
            "productCode": row.productCode,
            "productName": row.productName,
            "productLine": row.productLine,
            "quantityOrdered": row.quantity,
            "value": as_float(row.value),
        }
        for row in db.execute(stmt).all()
    ]


def orders_by_status(db: Session) -> list[dict]:
    stmt = select(Order.status.label("label"), func.count(Order.orderNumber).label("value")).group_by(Order.status)
    return [{"label": row.label, "value": row.value} for row in db.execute(stmt).all()]


def build_pivot(
    db: Session,
    *,
    row_dimension: str = "country",
    column_dimension: str = "year",
    metric: str = "sales_revenue",
) -> dict:
    row_map = {
        "country": Customer.country,
        "customer": Customer.customerName,
        "product_line": Product.productLine,
        "status": Order.status,
    }
    metric_map = {
        "sales_revenue": func.sum(order_total_expression()),
        "payments_received": func.sum(Payment.amount),
        "order_count": func.count(distinct(Order.orderNumber)),
        "quantity_ordered": func.sum(OrderDetail.quantityOrdered),
    }

    row_expr = row_map.get(row_dimension, Customer.country)
    metric_expr = metric_map.get(metric, func.sum(order_total_expression()))

    if metric == "payments_received":
        payment_column_map = {
            "year": extract("year", Payment.paymentDate),
            "month": func.date_format(Payment.paymentDate, "%Y-%m"),
        }
        payment_row_map = {
            "country": Customer.country,
            "customer": Customer.customerName,
        }
        row_expr = payment_row_map.get(row_dimension, Customer.country)
        column_expr = payment_column_map.get(column_dimension, extract("year", Payment.paymentDate))
        stmt = (
            select(row_expr.label("row_key"), column_expr.label("column_key"), metric_expr.label("value"))
            .select_from(Customer)
            .join(Payment, Payment.customerNumber == Customer.customerNumber)
            .group_by("row_key", "column_key")
            .order_by("row_key", "column_key")
        )
    else:
        column_map = {
            "year": extract("year", Order.orderDate),
            "month": func.date_format(Order.orderDate, "%Y-%m"),
            "status": Order.status,
            "product_line": Product.productLine,
        }
        column_expr = column_map.get(column_dimension, extract("year", Order.orderDate))
        stmt = (
            select(row_expr.label("row_key"), column_expr.label("column_key"), metric_expr.label("value"))
            .select_from(Order)
            .join(Customer, Customer.customerNumber == Order.customerNumber)
            .join(OrderDetail, OrderDetail.orderNumber == Order.orderNumber)
            .join(Product, Product.productCode == OrderDetail.productCode)
            .group_by("row_key", "column_key")
            .order_by("row_key", "column_key")
        )

    matrix: dict[str, dict[str, float]] = defaultdict(dict)
    columns: list[str] = []
    row_keys: list[str] = []
    seen_columns = set()

    for row in db.execute(stmt).all():
        row_key = str(row.row_key)
        column_key = str(row.column_key)
        if row_key not in matrix:
            row_keys.append(row_key)
        if column_key not in seen_columns:
            columns.append(column_key)
            seen_columns.add(column_key)
        matrix[row_key][column_key] = as_float(row.value)

    rows = []
    for row_key in row_keys:
        values = [matrix[row_key].get(column_key, 0) for column_key in columns]
        rows.append({"rowKey": row_key, "values": values, "total": sum(values)})

    return {"columns": columns, "rows": rows}


def get_lookups(db: Session) -> dict:
    countries = db.scalars(select(Customer.country).distinct().order_by(Customer.country)).all()
    cities = db.scalars(select(Customer.city).distinct().order_by(Customer.city)).all()
    sales_reps = db.execute(
        select(Employee.employeeNumber, Employee.firstName, Employee.lastName)
        .join(Customer, Customer.salesRepEmployeeNumber == Employee.employeeNumber)
        .distinct()
        .order_by(Employee.firstName, Employee.lastName)
    ).all()
    statuses = db.scalars(select(Order.status).distinct().order_by(Order.status)).all()
    product_lines = db.scalars(select(ProductLine.productLine).order_by(ProductLine.productLine)).all()

    return {
        "countries": countries,
        "cities": cities,
        "statuses": statuses,
        "productLines": product_lines,
        "salesReps": [
            {
                "employeeNumber": row.employeeNumber,
                "fullName": f"{row.firstName} {row.lastName}",
            }
            for row in sales_reps
        ],
    }
