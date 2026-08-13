# Task API

A minimal but complete REST API built with FastAPI. Demonstrates CRUD operations, validation, and proper HTTP status codes.

## Quick Start

**Install & run in one command:**

```bash
pip install fastapi uvicorn && python -m uvicorn myapi:app --host 127.0.0.1 --port 8000
```

Then visit:

- **API Docs (Swagger UI):** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

---

## Endpoints

| Method | Path          | Description        | Status     | Body                          |
| ------ | ------------- | ------------------ | ---------- | ----------------------------- |
| GET    | `/`           | Home endpoint      | 200        | `{"message":"Hello, World!"}` |
| GET    | `/health`     | Health check       | 200        | `{"status":"ok"}`             |
| GET    | `/tasks`      | List all tasks     | 200        | Array of tasks                |
| POST   | `/tasks`      | Create a new task  | 201        | New task object               |
| GET    | `/tasks/{id}` | Get one task by id | 200 or 404 | Task or error                 |
| PUT    | `/tasks/{id}` | Update a task      | 200 or 404 | Updated task or error         |
| DELETE | `/tasks/{id}` | Delete a task      | 204 or 404 | Empty or error                |

---

## Example: List All Tasks

```bash
$ curl -i http://localhost:8000/tasks
HTTP/1.1 200 OK
date: Thu, 13 Aug 2026 16:19:32 GMT
server: uvicorn
content-length: 66
content-type: application/json

[{"id":1,"done":false},{"id":2,"done":true},{"id":3,"done":false}]
```

---

## Create a Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

**Response (201 Created):**

```json
{ "id": 4, "title": "Buy milk", "done": false }
```

---

## Update a Task

```bash
curl -X PUT http://localhost:8000/tasks/4 \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","done":true}'
```

**Response (200 OK):**

```json
{ "id": 4, "title": "Buy milk", "done": true }
```

---

## Delete a Task

```bash
curl -X DELETE http://localhost:8000/tasks/4
```

**Response (204 No Content):** Empty body, success.

---

## Interactive Testing

Open **http://localhost:8000/docs** in your browser to test all endpoints via Swagger UI with the "Try it out" button.

### Swagger UI Examples

#### POST /tasks — Create a Task (201 Created)

Click "Try it out", enter `{"title":"hello everyone!"}` in the request body, and execute:

![POST /tasks - Create Task](./readme_assets/01_post_create_task.png)

```json
Request body:
{"title":"hello everyone!"}

Response (201 Created):
{"id":4,"title":"hello everyone!","done":false}
```

The response shows `201 Created` with the new task including an auto-assigned `id` and `done: false`.

---

#### PUT /tasks/{task_id} — Update a Task (200 OK)

Click the PUT endpoint, enter task ID `1` and new values like `{"title":"hello world it's me!","done":false}`:

![PUT /tasks - Update Task](./readme_assets/02_put_update_task.png)

```json
Request:
PUT /tasks/1
{"title":"hello world it's me!","done":false}

Response (200 OK):
{"id":1,"title":"hello world it's me!","done":false}
```

The response shows `200 OK` with the updated task object.

---

#### DELETE /tasks/{task_id} — Delete a Task (204 No Content)

Click the DELETE endpoint, enter task ID `1`, and execute:

![DELETE /tasks - Delete Task](./readme_assets/03_delete_remove_task.png)

```bash
DELETE /tasks/1

Response (204 No Content):
(empty body - success)
```

The response shows `204 No Content` — no body, which signals success. Follow up with `GET /tasks` to confirm deletion.

---

#### GET /tasks/{task_id} — Fetch a Single Task

Enter a valid task ID (e.g., `1`) to get `200 OK`:

![GET /tasks/{id} - Fetch Single Task](./readme_assets/04_get_single_task.png)

```json
Response (200 OK):
{"id":1,"done":false}
```

Enter an invalid ID (e.g., `0`) to see validation error `422 Unprocessable Content`:

![GET /tasks/{id} - Validation Error](./readme_assets/05_get_validation_error.png)

```json
Response (422 Unprocessable Content):
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["path", "task_id"],
      "msg": "Input should be greater than 0",
      "input": "0",
      "ctx": {"gt": 0}
    }
  ]
}
```

---

**Live curl commands:** Swagger UI automatically generates and displays the curl command for each request, making it easy to copy exact commands for scripting or documentation.

---

## Validation

- **Missing/empty title:** POST/PUT return `400 Bad Request`
- **Unknown id:** GET/PUT/DELETE return `404 Not Found`
- All responses include proper HTTP status codes for machine-readable errors

---

## Tech Stack

- **Framework:** FastAPI
- **Server:** Uvicorn
- **Language:** Python 3.13+
- **Docs:** Auto-generated Swagger UI (OpenAPI 3.1)
