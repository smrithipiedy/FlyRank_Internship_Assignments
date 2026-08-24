# Task API — Database Project

A simple Task API backed by a SQLite database, implementing full CRUD operations.

## Getting Started

### Run the Project
To start the server, run the following command from the `Week-3_A2` directory:
```bash
uvicorn myapi:app --host 127.0.0.1 --port 3000
```
Once the server is running, you can access the interactive API documentation at `http://127.0.0.1:3000/docs`.

### Database Setup
The project uses **SQLite**, which was chosen because it is a serverless, single-file database that requires zero setup and ensures data survives server restarts.

The database file lives at `tasks.db` in the project root. It is created automatically upon the first run of the application. It is listed in `.gitignore` so that every user who clones the repository starts with a fresh, automatically seeded database.

## Database Verification
Below is a screenshot of the database open in DB Browser for SQLite, showing the `tasks` table.

![Database Screenshot](readme_assets/tasks-table-screenshot.png)

### Example SQL Query (from Stage 4)
During Stage 4, I explored direct database manipulation. Here is an example query used to clean up completed tasks:

```sql
DELETE FROM tasks WHERE done = 1;
```
This query deleted all rows where the `done` column was set to 1, proving that changes made directly to the `.db` file are immediately reflected in the API responses.
