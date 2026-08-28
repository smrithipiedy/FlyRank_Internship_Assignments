# Task Management API (SQLite Version)

A simple REST API for managing a task list, built with FastAPI and SQLite. This project is containerized using Docker for easy deployment and persistence.

## Quick Start

Run the entire stack with one command:

```bash
docker compose up -d
```

## Configuration

The application uses environment variables for configuration. 
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` if you need to change the database storage path (default is `/app/data/tasks.db` inside the container).

## API Endpoints

| Method | Endpoint | Description | Success Code | Error Code |
| :--- | :--- | :--- | :--- | :--- |
| GET | `/tasks` | List all tasks | 200 OK | - |
| GET | `/tasks/{id}` | Get a specific task by ID | 200 OK | 404 Not Found |
| POST | `/tasks` | Create a new task | 201 Created | 400 Bad Request |
| PUT | `/tasks/{id}` | Update a task | 200 OK | 400 / 404 |
| DELETE | `/tasks/{id}` | Delete a task | 204 No Content | 404 Not Found |

## Sample Output

### GET /tasks
```text
HTTP/1.1 200 OK
date: Fri, 28 Aug 2026 16:02:21 GMT
server: uvicorn
content-length: 179
content-type: application/json

[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Finish homework","done":false},{"id":3,"title":"Call mom","done":false},{"id":4,"title":"Persistent Task","done":false}]
```

## Database Verification

To verify the data in the SQLite database:
1. Enter the container: `docker exec -it <container_id> sh`
2. Open the database: `sqlite3 /app/data/tasks.db`
3. Run the query: `SELECT * FROM tasks;`

*(Insert screenshot here showing the output of the SELECT query)*
