from __future__ import annotations

import os
import sqlite3

from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from init_db import init_db

# Make sure the schema exists and the three example rows are seeded before
# the first request lands. Safe to call on every boot.
init_db()

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.db")

app = FastAPI()


class TaskIn(BaseModel):
    """Payload accepted by POST /tasks."""
    title: str = Field(..., min_length=1)


class TaskUpdate(BaseModel):
    """Payload accepted by PUT /tasks/{id}.

    Either field is optional so callers can update just the title, just
    `done`, or both. Empty/whitespace-only titles are rejected.
    """
    title: str | None = Field(default=None, min_length=1)
    done: bool | None = None


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


@app.post("/tasks", summary="Create a new task", status_code=201)
def create_task(payload: TaskIn):
    """Insert a new task and return it."""
    title = payload.title.strip()
    if not title:
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"},
        )

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, 0),
        )
        conn.commit()
        new_id = cur.lastrowid
        row = cur.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (new_id,),
        ).fetchone()
    finally:
        conn.close()

    return _row_to_dict(row)


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    """Update an existing task. Returns 404 if no such task exists."""
    if payload.title is None and payload.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "At least one field (title or done) is required"},
        )

    title = payload.title.strip() if payload.title is not None else None
    if title is not None and title == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be empty"},
        )

    conn = get_connection()
    try:
        cur = conn.cursor()
        existing = cur.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        if existing is None:
            return JSONResponse(
                status_code=404,
                content={"error": "Task not found"},
            )

        sets: list[str] = []
        params: list = []
        if title is not None:
            sets.append("title = ?")
            params.append(title)
        if payload.done is not None:
            sets.append("done = ?")
            params.append(1 if payload.done else 0)
        params.append(task_id)

        cur.execute(
            f"UPDATE tasks SET {', '.join(sets)} WHERE id = ?",
            params,
        )
        conn.commit()

        updated = cur.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    finally:
        conn.close()

    return _row_to_dict(updated)


@app.delete("/tasks/{task_id}", summary="Delete a task", status_code=204)
def delete_task(task_id: int):
    """Delete a task by id. Returns 204 on success, 404 if no such task."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        deleted = cur.rowcount
    finally:
        conn.close()

    if deleted == 0:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )

    return JSONResponse(status_code=204, content=None)
