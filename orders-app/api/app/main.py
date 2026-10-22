import os
import time
from typing import Generator

import psycopg
from fastapi import Depends, FastAPI, HTTPException
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from pydantic import BaseModel, Field
from starlette.responses import Response

app = FastAPI(title="Orders API", version="1.0.0")
REQUESTS = Counter("orders_api_requests_total", "Orders API requests", ["operation"])


class OrderCreate(BaseModel):
    customer: str = Field(min_length=1, max_length=120)
    item: str = Field(min_length=1, max_length=120)
    quantity: int = Field(gt=0, le=1000)


class Order(OrderCreate):
    id: int


def database_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql://orders:orders@localhost:5432/orders")


def connection() -> Generator[psycopg.Connection, None, None]:
    with psycopg.connect(database_url()) as conn:
        yield conn


@app.on_event("startup")
def initialise_database() -> None:
    deadline = time.time() + 30
    while True:
        try:
            with psycopg.connect(database_url()) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        id SERIAL PRIMARY KEY,
                        customer VARCHAR(120) NOT NULL,
                        item VARCHAR(120) NOT NULL,
                        quantity INTEGER NOT NULL CHECK (quantity > 0)
                    )
                """)
                conn.commit()
            return
        except psycopg.OperationalError:
            if time.time() >= deadline:
                raise
            time.sleep(2)


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readiness() -> dict[str, str]:
    try:
        with psycopg.connect(database_url(), connect_timeout=2) as conn:
            conn.execute("SELECT 1")
        return {"status": "ready"}
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/orders", response_model=list[Order])
def list_orders(conn: psycopg.Connection = Depends(connection)) -> list[Order]:
    REQUESTS.labels("list").inc()
    rows = conn.execute("SELECT id, customer, item, quantity FROM orders ORDER BY id").fetchall()
    return [Order(id=r[0], customer=r[1], item=r[2], quantity=r[3]) for r in rows]


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int, conn: psycopg.Connection = Depends(connection)) -> Order:
    REQUESTS.labels("get").inc()
    row = conn.execute(
        "SELECT id, customer, item, quantity FROM orders WHERE id = %s", (order_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="order not found")
    return Order(id=row[0], customer=row[1], item=row[2], quantity=row[3])


@app.post("/orders", response_model=Order, status_code=201)
def create_order(payload: OrderCreate, conn: psycopg.Connection = Depends(connection)) -> Order:
    REQUESTS.labels("create").inc()
    row = conn.execute(
        "INSERT INTO orders (customer, item, quantity) VALUES (%s, %s, %s) "
        "RETURNING id, customer, item, quantity",
        (payload.customer, payload.item, payload.quantity),
    ).fetchone()
    conn.commit()
    return Order(id=row[0], customer=row[1], item=row[2], quantity=row[3])
