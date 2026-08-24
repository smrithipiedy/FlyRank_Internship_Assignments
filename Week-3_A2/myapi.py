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

    `done` is stored as INTEGER (0/1) in SQLite; coerce to a real bool so the
    JSON looks like `{"done": false}` instead of `{"done": 0}`.
    """
    if row is None:
        return None
    d = dict(row)
    d["done"] = bool(d["done"])
    return d


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
        return [_row_to_dict(row) for row in rows]
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

    return _row_to_dict(row)


@app.post("/tasks", summary="Create a new task", status_code=201)
def create_task(payload: TaskIn):
    """Insert a new task and return it (with the id the database assigned).

    Validation is handled by Pydantic: an empty/whitespace-only title is
    rejected with 422 before this function runs. We also defend against the
    `{"title": ""}` edge case explicitly so the client sees 400, matching
    Assignment 1's behaviour.
    """
    title = payload.title.strip()
    if not title:
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"},
        )

    conn = get_connection()
    try:
        cur = conn.cursor()
        # Let SQLite assign the id via AUTOINCREMENT. We pass `0` for `done`
        # (the column default) — explicitly here so the intent is obvious.
        cur.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, 0),
        )
        conn.commit()
        new_id = cur.lastrowid
        # Read back the row we just wrote so the response matches what the
        # client will see from GET /tasks/{id}.
        row = cur.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (new_id,),
        ).fetchone()
    finally:
        conn.close()

    return _row_to_dict(row)


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    """Update an existing task. Returns 404 if no such task exists.

    Validation matches Assignment 1:
      * at least one of `title` or `done` must be provided
      * `title`, if provided, cannot be empty/whitespace-only
      * `done`, if provided, must be a real boolean
    """
    # Refuse empty payloads before touching the database.
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
        # Confirm the row exists first so we can distinguish "not found"
        # from "nothing changed". `rowcount` alone can't tell us that.
        existing = cur.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        if existing is None:
            return JSONResponse(
                status_code=404,
                content={"error": "Task not found"},
            )

        # Build the UPDATE dynamically based on which fields were supplied.
        # We still pass every value as a parameter — never concatenated.
        sets: list[str] = []
        params: list = []
        if title is not None:
            sets.append("title = ?")
            params.append(title)
        if payload.done is not None:
            sets.append("done = ?")
            # Store as integer (0/1) to match the column type.
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

    # 204 No Content — empty body, same as Assignment 1.
    return JSONResponse(status_code=204, content=None)
