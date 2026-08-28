# Week 3 Assignment 3

## Setup

### Database
Run the following command to start Postgres in Docker:

```bash
docker run --name taskdb -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=tasks -p 5433:5432 -v taskdata:/var/lib/postgresql/data -d postgres:16
```

## Checkpoint
- [ ] Docker Postgres container is running (`docker ps`).
- [ ] Able to open SQL prompt (`docker exec -it taskdb psql -U postgres -d tasks`).
