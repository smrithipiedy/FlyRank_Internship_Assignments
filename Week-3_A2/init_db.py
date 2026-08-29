from __future__ import annotations

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.db")

EXAMPLE_TASKS = [
    ("Buy milk", 0),
    ("Finish homework", 0),
    ("Call mom", 0),
]


def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        # 1. Create the table if it doesn't already exist.
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT    NOT NULL,
                done  INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()

        # 2. Seed three example tasks only when the table is empty.
        cur.execute("SELECT COUNT(*) FROM tasks")
        (row_count,) = cur.fetchone()
        if row_count == 0:
            cur.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                EXAMPLE_TASKS,
            )
            conn.commit()
            print(f"Seeded {len(EXAMPLE_TASKS)} example tasks into {db_path}")
        else:
            print(f"Tasks table already populated ({row_count} rows); skipping seed.")
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
