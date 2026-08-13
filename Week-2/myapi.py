from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse

app = FastAPI()

# In-memory list of task objects (pre-filled with 3 examples)
tasks = [
    {"id": 1, "done": False},
    {"id": 2, "done": True},
    {"id": 3, "done": False},
]

@app.get("/")
def index():
    return {"message": "Hello, World!"}


@app.get("/get-tasks/{tasks_id}")
def get_tasks(tasks_id: int = Path(..., description="The ID of the task to retrieve", gt=0)):
    # Keep backward-compatible route: interpret as task id lookup
    for t in tasks:
        if t["id"] == tasks_id:
            return t
    return JSONResponse(status_code=404, content={"error": f"Task {tasks_id} not found"})


@app.get("/tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int = Path(..., description="The ID of the task to retrieve", gt=0)):
    for t in tasks:
        if t["id"] == task_id:
            return t
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks")
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
