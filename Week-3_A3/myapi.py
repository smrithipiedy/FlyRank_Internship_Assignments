from __future__ import annotations

from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse

from database import get_connection, init_db

# Ensure the schema exists and the three example rows are seeded before
# the first request lands.
init_db()

app = FastAPI()


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
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks")
            rows = cur.fetchall()
            # RealDictCursor returns dict-like objects, which FastAPI can serialize.
            return rows
    finally:
        conn.close()


@app.get("/tasks/{task_id}", summary="Get one task by id")
def get_task(task_id: int = Path(..., description="The ID of the task to retrieve", gt=0)):
    """Fetch one row by id. Returns 404 if no such task exists."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Parameterized query — `%s` is the placeholder for psycopg2.
            cur.execute(
                "SELECT * FROM tasks WHERE id = %s",
                (task_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )

    return row
