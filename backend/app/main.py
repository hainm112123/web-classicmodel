from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import customers, dashboard, lookups, orders, reports
from app.core.config import settings


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(lookups.router, prefix="/api")


@app.get("/health")
def healthcheck():
    return {"status": "ok"}

