from fastapi import FastAPI, Path

app = FastAPI()

tasks = {
    1:{ "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }
}

@app.get("/")
def index():
    return {"message": "Hello, World!"}


@app.get("/get-tasks/{tasks_id}")
def get_tasks(tasks_id: int = Path(..., description="The ID of the task to retrieve", gt=0)):
    return tasks[tasks_id]


@app.get("/health")
def health():
    return {"status": "ok"}
