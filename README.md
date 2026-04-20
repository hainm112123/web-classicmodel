# Classic Models Analytics

Full-stack analytics website for the Classic Models sample database.

## Stack

- Backend: FastAPI, SQLAlchemy ORM, REST API
- Frontend: React, TypeScript, Vite
- Database: MySQL
- Environment: Docker Compose

## Features

- Search customers and orders
- Revenue, payment, and order statistics
- Dashboard charts
- Pivot table style report view
- Customer detail with orders and payments
- Order detail with line items and totals

## Run

1. Copy `.env.example` to `.env` if you want to override defaults.
2. Start the stack:

```bash
docker compose up --build
```

3. Open:
- Frontend: `http://localhost:5173`
- Backend API docs: `http://localhost:8000/docs`

## Notes

- The database initializes from `mysqlsampledatabase.sql` on first container startup.
- If you need to re-import the database from scratch, remove the `mysql_data` volume before restarting.
