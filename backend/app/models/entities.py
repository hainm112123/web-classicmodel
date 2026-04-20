from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, SmallInteger, String, Text
from sqlalchemy.dialects.mysql import MEDIUMBLOB, MEDIUMTEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ProductLine(Base):
    __tablename__ = "productlines"

    productLine: Mapped[str] = mapped_column(String(50), primary_key=True)
    textDescription: Mapped[str | None] = mapped_column(String(4000))
    htmlDescription: Mapped[str | None] = mapped_column(MEDIUMTEXT)
    image: Mapped[bytes | None] = mapped_column(MEDIUMBLOB)

    products: Mapped[list["Product"]] = relationship(back_populates="productLineRef")


class Product(Base):
    __tablename__ = "products"

    productCode: Mapped[str] = mapped_column(String(15), primary_key=True)
    productName: Mapped[str] = mapped_column(String(70))
    productLine: Mapped[str] = mapped_column(ForeignKey("productlines.productLine"))
    productScale: Mapped[str] = mapped_column(String(10))
    productVendor: Mapped[str] = mapped_column(String(50))
    productDescription: Mapped[str] = mapped_column(Text)
    quantityInStock: Mapped[int] = mapped_column(SmallInteger)
    buyPrice: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    MSRP: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    productLineRef: Mapped["ProductLine"] = relationship(back_populates="products")
    orderDetails: Mapped[list["OrderDetail"]] = relationship(back_populates="product")


class Office(Base):
    __tablename__ = "offices"

    officeCode: Mapped[str] = mapped_column(String(10), primary_key=True)
    city: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(50))
    addressLine1: Mapped[str] = mapped_column(String(50))
    addressLine2: Mapped[str | None] = mapped_column(String(50))
    state: Mapped[str | None] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(50))
    postalCode: Mapped[str] = mapped_column(String(15))
    territory: Mapped[str] = mapped_column(String(10))

    employees: Mapped[list["Employee"]] = relationship(back_populates="office")


class Employee(Base):
    __tablename__ = "employees"

    employeeNumber: Mapped[int] = mapped_column(Integer, primary_key=True)
    lastName: Mapped[str] = mapped_column(String(50))
    firstName: Mapped[str] = mapped_column(String(50))
    extension: Mapped[str] = mapped_column(String(10))
    email: Mapped[str] = mapped_column(String(100))
    officeCode: Mapped[str] = mapped_column(ForeignKey("offices.officeCode"))
    reportsTo: Mapped[int | None] = mapped_column(ForeignKey("employees.employeeNumber"))
    jobTitle: Mapped[str] = mapped_column(String(50))

    office: Mapped["Office"] = relationship(back_populates="employees")
    manager: Mapped["Employee | None"] = relationship(remote_side=[employeeNumber], back_populates="directReports")
    directReports: Mapped[list["Employee"]] = relationship(back_populates="manager")
    customers: Mapped[list["Customer"]] = relationship(back_populates="salesRep")


class Customer(Base):
    __tablename__ = "customers"

    customerNumber: Mapped[int] = mapped_column(Integer, primary_key=True)
    customerName: Mapped[str] = mapped_column(String(50))
    contactLastName: Mapped[str] = mapped_column(String(50))
    contactFirstName: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(50))
    addressLine1: Mapped[str] = mapped_column(String(50))
    addressLine2: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(50))
    state: Mapped[str | None] = mapped_column(String(50))
    postalCode: Mapped[str | None] = mapped_column(String(15))
    country: Mapped[str] = mapped_column(String(50))
    salesRepEmployeeNumber: Mapped[int | None] = mapped_column(ForeignKey("employees.employeeNumber"))
    creditLimit: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    salesRep: Mapped["Employee | None"] = relationship(back_populates="customers")
    payments: Mapped[list["Payment"]] = relationship(back_populates="customer")
    orders: Mapped[list["Order"]] = relationship(back_populates="customer")


class Payment(Base):
    __tablename__ = "payments"

    customerNumber: Mapped[int] = mapped_column(ForeignKey("customers.customerNumber"), primary_key=True)
    checkNumber: Mapped[str] = mapped_column(String(50), primary_key=True)
    paymentDate: Mapped[date] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    customer: Mapped["Customer"] = relationship(back_populates="payments")


class Order(Base):
    __tablename__ = "orders"

    orderNumber: Mapped[int] = mapped_column(Integer, primary_key=True)
    orderDate: Mapped[date] = mapped_column(Date)
    requiredDate: Mapped[date] = mapped_column(Date)
    shippedDate: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(15))
    comments: Mapped[str | None] = mapped_column(Text)
    customerNumber: Mapped[int] = mapped_column(ForeignKey("customers.customerNumber"))

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    details: Mapped[list["OrderDetail"]] = relationship(back_populates="order")


class OrderDetail(Base):
    __tablename__ = "orderdetails"

    orderNumber: Mapped[int] = mapped_column(ForeignKey("orders.orderNumber"), primary_key=True)
    productCode: Mapped[str] = mapped_column(ForeignKey("products.productCode"), primary_key=True)
    quantityOrdered: Mapped[int] = mapped_column(Integer)
    priceEach: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    orderLineNumber: Mapped[int] = mapped_column(SmallInteger)

    order: Mapped["Order"] = relationship(back_populates="details")
    product: Mapped["Product"] = relationship(back_populates="orderDetails")

