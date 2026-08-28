from __future__ import annotations

import os
import sqlite3

from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse

from init_db import init_db

# Make sure the schema exists and the three example rows are seeded before
# the first request lands. Safe to call on every boot.
init_db()

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.db")

app = FastAPI()


def _row_to_dict(row: sqlite3.Row | None) -> dict | None:
    """Convert a sqlite3.Row into the JSON shape the API returns.
    `done` is stored as INTEGER (0/1) in SQLite; coerce to a real bool.
    """
    if row is None:
        return None
    d = dict(row)
    d["done"] = bool(d["done"])
    return d


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/", summary="Home endpoint")
def index():
    return {"message": "Hello, World!"}


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    """Read every task from the database and return it as JSON."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id, title, done FROM tasks").fetchall()
        return [_row_to_dict(row) for row in rows]
    finally:
        conn.close()


@app.get("/tasks/{task_id}", summary="Get one task by id")
def get_task(task_id: int = Path(..., description="The ID of the task to retrieve", gt=0)):
    """Fetch one row by id. Returns 404 if no such task exists."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )

    return _row_to_dict(row)
