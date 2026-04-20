import { NavLink, Outlet } from "react-router-dom";
import { Chatbot } from "./Chatbot";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/customers", label: "Customers" },
  { to: "/orders", label: "Orders" },
  { to: "/reports", label: "Reports" }
];

export function Layout() {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Classic Models</p>
          <h1>Analytics Hub</h1>
        </div>
        <nav className="nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
              end={item.to === "/"}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content">
        <Outlet />
      </main>
      <Chatbot />
    </div>
  );
}

