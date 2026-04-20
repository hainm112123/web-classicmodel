import { useEffect, useState } from "react";

import { fetchJson } from "../api/client";
import { ChartCard } from "../components/ChartCard";
import type { LabelValue, PivotResponse } from "../types/api";

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

export function ReportsPage() {
  const [countryRevenue, setCountryRevenue] = useState<LabelValue[]>([]);
  const [productLineRevenue, setProductLineRevenue] = useState<LabelValue[]>([]);
  const [topCustomers, setTopCustomers] = useState<{ customerName: string; value: number }[]>([]);
  const [topProducts, setTopProducts] = useState<{ productName: string; quantityOrdered: number; value: number }[]>([]);
  const [pivot, setPivot] = useState<PivotResponse | null>(null);
  const [rowDimension, setRowDimension] = useState("country");
  const [columnDimension, setColumnDimension] = useState("year");
  const [metric, setMetric] = useState("sales_revenue");

  useEffect(() => {
    Promise.all([
      fetchJson<LabelValue[]>("/reports/revenue-by-country"),
      fetchJson<LabelValue[]>("/reports/revenue-by-product-line"),
      fetchJson<{ customerName: string; value: number }[]>("/reports/top-customers"),
      fetchJson<{ productName: string; quantityOrdered: number; value: number }[]>("/reports/top-products")
    ]).then(([countryResponse, productLineResponse, customerResponse, productResponse]) => {
      setCountryRevenue(countryResponse);
      setProductLineRevenue(productLineResponse);
      setTopCustomers(customerResponse);
      setTopProducts(productResponse);
    });
  }, []);

  useEffect(() => {
    const params = new URLSearchParams({
      rowDimension,
      columnDimension,
      metric
    });
    fetchJson<PivotResponse>(`/reports/pivot?${params.toString()}`).then(setPivot);
  }, [rowDimension, columnDimension, metric]);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Reports</p>
          <h2>Revenue, ranking, and pivot analysis</h2>
        </div>
      </div>

      <section className="chart-grid">
        <ChartCard
          title="Revenue by Country"
          option={{
            color: ["#6366f1"],
            tooltip: { trigger: "axis" },
            grid: { left: "3%", right: "10%", bottom: "3%", containLabel: true },
            xAxis: { type: "value" },
            yAxis: { type: "category", data: countryRevenue.map((item) => item.label).reverse() },
            series: [{ type: "bar", data: countryRevenue.map((item) => item.value).reverse(), itemStyle: { borderRadius: [0, 4, 4, 0] } }]
          }}
        />
        <ChartCard
          title="Revenue by Product Line"
          option={{
            tooltip: { trigger: "item" },
            legend: { bottom: "0%", left: "center" },
            series: [
              {
                type: "pie",
                radius: ["50%", "70%"],
                itemStyle: { borderRadius: 10, borderColor: "#fff", borderWidth: 2 },
                data: productLineRevenue.map((item) => ({ name: item.label, value: item.value }))
              }
            ]
          }}
        />
      </section>

      <div className="split-layout">
        <section className="card">
          <div className="section-head">
            <h2>Top customers</h2>
          </div>
          <table className="data-table compact-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Revenue</th>
              </tr>
            </thead>
            <tbody>
              {topCustomers.map((row) => (
                <tr key={row.customerName}>
                  <td>{row.customerName}</td>
                  <td>{formatCurrency(row.value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="card">
          <div className="section-head">
            <h2>Top products</h2>
          </div>
          <table className="data-table compact-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Qty</th>
                <th>Revenue</th>
              </tr>
            </thead>
            <tbody>
              {topProducts.map((row) => (
                <tr key={row.productName}>
                  <td>{row.productName}</td>
                  <td>{row.quantityOrdered}</td>
                  <td>{formatCurrency(row.value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>

      <section className="card">
        <div className="section-head">
          <h2>Pivot table</h2>
        </div>
        <div className="filter-bar filter-bar-inline">
          <select value={rowDimension} onChange={(event) => setRowDimension(event.target.value)}>
            <option value="country">Rows: Country</option>
            <option value="customer">Rows: Customer</option>
            <option value="product_line">Rows: Product Line</option>
            <option value="status">Rows: Status</option>
          </select>
          <select value={columnDimension} onChange={(event) => setColumnDimension(event.target.value)}>
            <option value="year">Columns: Year</option>
            <option value="month">Columns: Month</option>
            <option value="status">Columns: Status</option>
            <option value="product_line">Columns: Product Line</option>
          </select>
          <select value={metric} onChange={(event) => setMetric(event.target.value)}>
            <option value="sales_revenue">Metric: Sales revenue</option>
            <option value="order_count">Metric: Order count</option>
            <option value="quantity_ordered">Metric: Quantity ordered</option>
            <option value="payments_received">Metric: Payments received</option>
          </select>
        </div>
        {pivot && (
          <table className="data-table pivot-table">
            <thead>
              <tr>
                <th>Row</th>
                {pivot.columns.map((column) => (
                  <th key={column}>{column}</th>
                ))}
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {pivot.rows.map((row) => (
                <tr key={row.rowKey}>
                  <td>{row.rowKey}</td>
                  {row.values.map((value, index) => (
                    <td key={`${row.rowKey}-${pivot.columns[index]}`}>{metric === "sales_revenue" || metric === "payments_received" ? formatCurrency(value) : value}</td>
                  ))}
                  <td>{metric === "sales_revenue" || metric === "payments_received" ? formatCurrency(row.total) : row.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}

