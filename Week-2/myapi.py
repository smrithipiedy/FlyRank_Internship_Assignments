from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse

app = FastAPI()

# In-memory list of task objects (pre-filled with 3 examples)
tasks = [
    {"id": 1, "done": False},
    {"id": 2, "done": True},
    {"id": 3, "done": False},
]

@app.get("/", summary="Home endpoint")
def index():
    return {"message": "Hello, World!"}


@app.get("/get-tasks/{tasks_id}", summary="Get a task by id (legacy route)")
def get_tasks(tasks_id: int = Path(..., description="The ID of the task to retrieve", gt=0)):
    # Keep backward-compatible route: interpret as task id lookup
    for t in tasks:
        if t["id"] == tasks_id:
            return t
    return JSONResponse(status_code=404, content={"error": f"Task {tasks_id} not found"})


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get one task by id")
def get_task(task_id: int = Path(..., description="The ID of the task to retrieve", gt=0)):
    for t in tasks:
        if t["id"] == task_id:
            return t
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.post("/tasks", summary="Create a new task")
def create_task(task: dict):
    title = task.get("title") if isinstance(task, dict) else None

    if title is None or not isinstance(title, str) or title.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"},
        )

    new_task = {"id": max((t["id"] for t in tasks), default=0) + 1, "title": title.strip(), "done": False}
    tasks.append(new_task)
    return JSONResponse(status_code=201, content=new_task)


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, task: dict):
    if not isinstance(task, dict):
        return JSONResponse(status_code=400, content={"error": "Request body must be a JSON object"})

    title = task.get("title")
    done = task.get("done")

    if title is None and done is None:
        return JSONResponse(status_code=400, content={"error": "At least one field (title or done) is required"})

    if title is not None and (not isinstance(title, str) or title.strip() == ""):
        return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})

    if done is not None and not isinstance(done, bool):
        return JSONResponse(status_code=400, content={"error": "Done must be a boolean"})

    for i, existing in enumerate(tasks):
        if existing["id"] == task_id:
            updated = dict(existing)
            if title is not None:
                updated["title"] = title.strip()
            if done is not None:
                updated["done"] = done
            tasks[i] = updated
            return updated

    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})


@app.delete("/tasks/{task_id}", summary="Delete a task")
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            del tasks[i]
            return JSONResponse(status_code=204, content=None)

    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
