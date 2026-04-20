import { useEffect, useState } from "react";

import { fetchJson } from "../api/client";
import type { LookupResponse, OrderDetail, OrderRow, PaginatedResponse } from "../types/api";

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

export function OrdersPage() {
  const [orders, setOrders] = useState<OrderRow[]>([]);
  const [lookups, setLookups] = useState<LookupResponse | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<OrderDetail | null>(null);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetchJson<LookupResponse>("/lookups").then(setLookups);
  }, []);

  useEffect(() => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (status) params.set("status", status);
    fetchJson<PaginatedResponse<OrderRow>>(`/orders?${params.toString()}`).then((response) => {
      setOrders(response.items);
    });
  }, [search, status]);

  const loadOrder = async (orderNumber: number) => {
    const response = await fetchJson<OrderDetail>(`/orders/${orderNumber}`);
    setSelectedOrder(response);
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Orders</p>
          <h2>Search and drill down into order detail</h2>
        </div>
      </div>

      <section className="card filter-bar">
        <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by order number or customer" />
        <select value={status} onChange={(event) => setStatus(event.target.value)}>
          <option value="">All statuses</option>
          {lookups?.statuses.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </section>

      <div className="split-layout">
        <section className="card">
          <div className="section-head">
            <h2>Orders</h2>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Order</th>
                <th>Date</th>
                <th>Status</th>
                <th>Customer</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.orderNumber} onClick={() => loadOrder(order.orderNumber)} className="clickable">
                  <td>{order.orderNumber}</td>
                  <td>{order.orderDate}</td>
                  <td>{order.status}</td>
                  <td>{order.customerName}</td>
                  <td>{formatCurrency(order.total)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="card detail-panel">
          <div className="section-head">
            <h2>Order detail</h2>
          </div>
          {selectedOrder ? (
            <>
              <div className="detail-grid">
                <div>
                  <span>Order</span>
                  <strong>{selectedOrder.orderNumber}</strong>
                </div>
                <div>
                  <span>Customer</span>
                  <strong>{selectedOrder.customer.customerName}</strong>
                </div>
                <div>
                  <span>Status</span>
                  <strong>{selectedOrder.status}</strong>
                </div>
                <div>
                  <span>Total</span>
                  <strong>{formatCurrency(selectedOrder.total)}</strong>
                </div>
              </div>
              <table className="data-table compact-table">
                <thead>
                  <tr>
                    <th>Line</th>
                    <th>Product</th>
                    <th>Product line</th>
                    <th>Qty</th>
                    <th>Unit price</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedOrder.lines.map((line) => (
                    <tr key={`${line.orderLineNumber}-${line.productCode}`}>
                      <td>{line.orderLineNumber}</td>
                      <td>{line.productName}</td>
                      <td>{line.productLine}</td>
                      <td>{line.quantityOrdered}</td>
                      <td>{formatCurrency(line.priceEach)}</td>
                      <td>{formatCurrency(line.lineTotal)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          ) : (
            <p>Select an order to see line items and computed totals.</p>
          )}
        </section>
      </div>
    </div>
  );
}

