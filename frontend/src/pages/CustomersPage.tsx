import { useEffect, useState } from "react";

import { fetchJson } from "../api/client";
import type {
  CustomerDetail,
  CustomerOrder,
  CustomerPayment,
  CustomerRow,
  LookupResponse,
  PaginatedResponse
} from "../types/api";

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

export function CustomersPage() {
  const [customers, setCustomers] = useState<CustomerRow[]>([]);
  const [lookups, setLookups] = useState<LookupResponse | null>(null);
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerDetail | null>(null);
  const [orders, setOrders] = useState<CustomerOrder[]>([]);
  const [payments, setPayments] = useState<CustomerPayment[]>([]);
  const [search, setSearch] = useState("");
  const [country, setCountry] = useState("");

  useEffect(() => {
    fetchJson<LookupResponse>("/lookups").then(setLookups);
  }, []);

  useEffect(() => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (country) params.set("country", country);
    fetchJson<PaginatedResponse<CustomerRow>>(`/customers?${params.toString()}`).then((response) => {
      setCustomers(response.items);
    });
  }, [search, country]);

  const loadCustomer = async (customerNumber: number) => {
    const [detailResponse, ordersResponse, paymentsResponse] = await Promise.all([
      fetchJson<CustomerDetail>(`/customers/${customerNumber}`),
      fetchJson<CustomerOrder[]>(`/customers/${customerNumber}/orders`),
      fetchJson<CustomerPayment[]>(`/customers/${customerNumber}/payments`)
    ]);
    setSelectedCustomer(detailResponse);
    setOrders(ordersResponse);
    setPayments(paymentsResponse);
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Customers</p>
          <h2>Search and account performance</h2>
        </div>
      </div>

      <section className="card filter-bar">
        <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by customer name or number" />
        <select value={country} onChange={(event) => setCountry(event.target.value)}>
          <option value="">All countries</option>
          {lookups?.countries.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </section>

      <div className="split-layout">
        <section className="card">
          <div className="section-head">
            <h2>Customer list</h2>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Country</th>
                <th>City</th>
                <th>Orders</th>
                <th>Revenue</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr key={customer.customerNumber} onClick={() => loadCustomer(customer.customerNumber)} className="clickable">
                  <td>{customer.customerName}</td>
                  <td>{customer.country}</td>
                  <td>{customer.city}</td>
                  <td>{customer.orderCount}</td>
                  <td>{formatCurrency(customer.salesRevenue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="card detail-panel">
          <div className="section-head">
            <h2>Customer detail</h2>
          </div>
          {selectedCustomer ? (
            <>
              <div className="detail-grid">
                <div>
                  <span>Name</span>
                  <strong>{selectedCustomer.customerName}</strong>
                </div>
                <div>
                  <span>Contact</span>
                  <strong>{selectedCustomer.contactName}</strong>
                </div>
                <div>
                  <span>Sales rep</span>
                  <strong>{selectedCustomer.salesRepName ?? "Unassigned"}</strong>
                </div>
                <div>
                  <span>Outstanding balance</span>
                  <strong>{formatCurrency(selectedCustomer.outstandingBalance)}</strong>
                </div>
              </div>

              <h3>Orders</h3>
              <table className="data-table compact-table">
                <thead>
                  <tr>
                    <th>Order</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => (
                    <tr key={order.orderNumber}>
                      <td>{order.orderNumber}</td>
                      <td>{order.orderDate}</td>
                      <td>{order.status}</td>
                      <td>{formatCurrency(order.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <h3>Payments</h3>
              <table className="data-table compact-table">
                <thead>
                  <tr>
                    <th>Check</th>
                    <th>Date</th>
                    <th>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map((payment) => (
                    <tr key={`${payment.checkNumber}-${payment.paymentDate}`}>
                      <td>{payment.checkNumber}</td>
                      <td>{payment.paymentDate}</td>
                      <td>{formatCurrency(payment.amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          ) : (
            <p>Select a customer to see detail, order history, and payments.</p>
          )}
        </section>
      </div>
    </div>
  );
}

