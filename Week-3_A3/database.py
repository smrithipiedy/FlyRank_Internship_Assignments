from __future__ import annotations

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

EXAMPLE_TASKS = [
    ("Buy milk", False),
    ("Finish homework", False),
    ("Call mom", False),
]

def get_connection():
    """Returns a connection to the Postgres database."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found in environment variables")
    # Use RealDictCursor to get dictionary-like results
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db() -> None:
    """Create the schema (if missing) and seed example rows (only when empty)."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Create the table if it doesn't already exist.
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id    SERIAL PRIMARY KEY,
                        title TEXT    NOT NULL,
                        done  BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                conn.commit()

                # 2. Seed three example tasks only when the table is empty.
                cur.execute("SELECT COUNT(*) FROM tasks")
                result = cur.fetchone()
                row_count = result["count"] if result else 0

                if row_count == 0:
                    cur.executemany(
                        "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                        EXAMPLE_TASKS,
                    )
                    conn.commit()
                    print(f"Seeded {len(EXAMPLE_TASKS)} example tasks into Postgres")
                else:
                    print(f"Tasks table already populated ({row_count} rows); skipping seed.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise e

if __name__ == "__main__":
    init_db()
