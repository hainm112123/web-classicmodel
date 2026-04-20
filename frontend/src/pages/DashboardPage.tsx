import { useEffect, useState } from "react";

import { fetchJson } from "../api/client";
import { ChartCard } from "../components/ChartCard";
import { StatCard } from "../components/StatCard";
import type { LabelValue, RecentOrder, Summary, TimePoint } from "../types/api";

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

export function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [sales, setSales] = useState<TimePoint[]>([]);
  const [payments, setPayments] = useState<TimePoint[]>([]);
  const [statusData, setStatusData] = useState<LabelValue[]>([]);
  const [topCustomers, setTopCustomers] = useState<{ customerName: string; value: number }[]>([]);
  const [recentOrders, setRecentOrders] = useState<RecentOrder[]>([]);

  useEffect(() => {
    Promise.all([
      fetchJson<Summary>("/dashboard/summary"),
      fetchJson<TimePoint[]>("/dashboard/monthly-sales"),
      fetchJson<TimePoint[]>("/dashboard/monthly-payments"),
      fetchJson<LabelValue[]>("/dashboard/orders-by-status"),
      fetchJson<{ customerName: string; value: number }[]>("/dashboard/top-customers"),
      fetchJson<RecentOrder[]>("/dashboard/recent-orders")
    ]).then(([summaryResponse, salesResponse, paymentsResponse, statusResponse, topCustomersResponse, recentResponse]) => {
      setSummary(summaryResponse);
      setSales(salesResponse);
      setPayments(paymentsResponse);
      setStatusData(statusResponse);
      setTopCustomers(topCustomersResponse);
      setRecentOrders(recentResponse);
    });
  }, []);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Overview</p>
          <h2>Business dashboard</h2>
        </div>
      </div>

      <section className="stats-grid">
        <StatCard label="Customers" value={summary ? summary.customers.toString() : "..."} />
        <StatCard label="Orders" value={summary ? summary.orders.toString() : "..."} />
        <StatCard label="Sales revenue" value={summary ? formatCurrency(summary.salesRevenue) : "..."} />
        <StatCard label="Payments received" value={summary ? formatCurrency(summary.paymentsReceived) : "..."} />
        <StatCard label="Average order value" value={summary ? formatCurrency(summary.averageOrderValue) : "..."} />
      </section>

      <section className="chart-grid">
        <ChartCard
          title="Monthly Sales Revenue"
          option={{
            color: ["#6366f1"],
            tooltip: { trigger: "axis", backgroundColor: "rgba(255, 255, 255, 0.9)", borderWidth: 0, shadowBlur: 10 },
            grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
            xAxis: { type: "category", data: sales.map((item) => item.period), axisLine: { lineStyle: { color: "#e2e8f0" } } },
            yAxis: { type: "value", splitLine: { lineStyle: { type: "dashed", color: "#f1f5f9" } } },
            series: [{
              type: "line",
              smooth: true,
              data: sales.map((item) => item.value),
              areaStyle: {
                color: {
                  type: "linear",
                  x: 0, y: 0, x2: 0, y2: 1,
                  colorStops: [{ offset: 0, color: "rgba(99, 102, 241, 0.3)" }, { offset: 1, color: "rgba(99, 102, 241, 0)" }]
                }
              },
              lineStyle: { width: 3 }
            }]
          }}
        />
        <ChartCard
          title="Monthly Payments"
          option={{
            color: ["#f59e0b"],
            tooltip: { trigger: "axis" },
            grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
            xAxis: { type: "category", data: payments.map((item) => item.period) },
            yAxis: { type: "value" },
            series: [{ type: "bar", data: payments.map((item) => item.value), itemStyle: { borderRadius: [4, 4, 0, 0] } }]
          }}
        />
        <ChartCard
          title="Orders by Status"
          option={{
            tooltip: { trigger: "item" },
            legend: { bottom: "0%", left: "center" },
            series: [
              {
                type: "pie",
                radius: ["50%", "70%"],
                avoidLabelOverlap: false,
                itemStyle: { borderRadius: 10, borderColor: "#fff", borderWidth: 2 },
                label: { show: false, position: "center" },
                emphasis: { label: { show: true, fontSize: 16, fontWeight: "bold" } },
                data: statusData.map((item) => ({ name: item.label, value: item.value }))
              }
            ]
          }}
        />
        <ChartCard
          title="Top 5 Customers by Sales"
          option={{
            color: ["#10b981"],
            tooltip: { trigger: "axis" },
            grid: { left: "3%", right: "10%", bottom: "3%", containLabel: true },
            xAxis: { type: "value" },
            yAxis: { type: "category", data: topCustomers.map((item) => item.customerName).reverse() },
            series: [{ type: "bar", data: topCustomers.map((item) => item.value).reverse(), itemStyle: { borderRadius: [0, 4, 4, 0] } }]
          }}
        />
      </section>

      <section className="card">
        <div className="section-head">
          <h2>Recent orders</h2>
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
            {recentOrders.map((order) => (
              <tr key={order.orderNumber}>
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
    </div>
  );
}

