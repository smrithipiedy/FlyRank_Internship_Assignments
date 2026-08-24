# Task API — Stage 4

Stage 4: explored SQLite by running queries by hand against `tasks.db` and
confirming each change shows up through the running API with no restart.

## Query I ran

```sql
DELETE FROM tasks WHERE done = 1;
```

## What it returned

It deleted every row whose `done` column was 1 — in my run, 6 rows. After it
ran, `GET /tasks` from the API immediately returned `[]` with no server
restart. That proved the API and the SQLite file are reading the same source
of truth: a write in one place is visible everywhere instantly.

## Notes from the experiment

- `SELECT * FROM tasks WHERE done = 1` returned only the row that was already
  marked done (id=7 "Survive restart"), since every other row had `done = 0`.
- `UPDATE tasks SET done = 1` with no `WHERE` clause flipped every row at
  once. **Lesson:** an UPDATE without a WHERE affects every row in the table.
- `SELECT COUNT(*) FROM tasks` returned `6` — a single number, not a rowset.
- After deleting everything, re-seeding produced ids `8, 9, 10` instead of
  `1, 2, 3` because SQLite's AUTOINCREMENT counter persists even after rows
  are deleted. The ids are unique, which is what matters; the counter doesn't
  rewind.
