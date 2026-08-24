"""Task API backed by a SQLite database.

Stage 1 (Week-3_A2):
- Reads from `tasks.db` instead of an in-memory list.
- `GET /tasks`        -> SELECT * FROM tasks
- `GET /tasks/{id}`   -> SELECT * FROM tasks WHERE id = ?
- Unknown ids return 404 + `{"error": "Task not found"}`.

Run:
    uvicorn myapi:app --host 127.0.0.1 --port 3000
"""

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


def get_connection() -> sqlite3.Connection:
    # `row_factory` lets us address columns by name; `detect_types` is unused
    # here but harmless. We open a fresh connection per request — SQLite is
    # fine with that for an app of this size.
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
        # Row objects -> plain dicts so FastAPI can serialize them.
        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.get("/tasks/{task_id}", summary="Get one task by id")
def get_task(task_id: int = Path(..., description="The ID of the task to retrieve", gt=0)):
    """Fetch one row by id. Returns 404 if no such task exists."""
    conn = get_connection()
    try:
        # Parameterized query — `?` is a placeholder; the id is passed
        # separately so user input can never become part of the SQL string.
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

    return dict(row)
