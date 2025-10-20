# Todo CRUD API

A simple CRUD API built with FastAPI and PostgreSQL, using UV as package manager and Alembic for database migrations.

## Features

- FastAPI framework for building REST APIs
- PostgreSQL database
- SQLAlchemy ORM
- Alembic for database migrations
- UV for fast dependency management
- Full CRUD operations for todos

## Project Structure

```
simple-crud/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── todo.py          # Todo SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── todo.py          # Pydantic schemas
│   ├── crud/
│   │   ├── __init__.py
│   │   └── todo.py          # CRUD operations
│   └── api/
│       ├── __init__.py
│       └── todos.py         # API endpoints
├── alembic/                 # Database migrations
├── .env                     # Environment variables
└── pyproject.toml          # Project dependencies
```

## Prerequisites

- Python 3.13+
- PostgreSQL
- UV package manager

## Setup

1. **Clone the repository**

2. **Set up PostgreSQL database**

Create a PostgreSQL database and user:

```sql
CREATE DATABASE todo_db;
CREATE USER strapi WITH PASSWORD 'strapi_password';
GRANT ALL PRIVILEGES ON DATABASE todo_db TO strapi;
```

3. **Configure environment variables**

Update the `.env` file with your database credentials:

```env
DATABASE_URL=postgresql://strapi:strapi_password@localhost:5432/todo_db
```

4. **Install dependencies**

UV will automatically install dependencies when running commands, but you can also install them explicitly:

```bash
uv sync
```

5. **Run database migrations**

```bash
uv run alembic upgrade head
```

6. **Run the application**

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Makefile Commands

For convenience, you can use the Makefile commands:

```bash
make help              # Show all available commands
make install           # Install dependencies
make run               # Run the development server
make migrate-upgrade   # Apply database migrations
make migrate-create MSG='description'  # Create new migration
make migrate-downgrade # Rollback last migration
make clean             # Remove cache files
make dev               # Install, migrate, and run (full setup)
```

Quick start with Makefile:
```bash
make install
make migrate-upgrade
make run
```

## API Endpoints

### Root

- `GET /` - Welcome message
- `GET /health` - Health check

### Todos

- `POST /api/todos/` - Create a new todo
- `GET /api/todos/` - Get all todos (with pagination)
- `GET /api/todos/{todo_id}` - Get a specific todo
- `PUT /api/todos/{todo_id}` - Update a todo
- `DELETE /api/todos/{todo_id}` - Delete a todo

## API Documentation

Once the server is running, you can access:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Requests

### Create a Todo

```bash
curl -X POST "http://localhost:8000/api/todos/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false
  }'
```

### Get All Todos

```bash
curl "http://localhost:8000/api/todos/"
```

### Get a Specific Todo

```bash
curl "http://localhost:8000/api/todos/1"
```

### Update a Todo

```bash
curl -X PUT "http://localhost:8000/api/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

### Delete a Todo

```bash
curl -X DELETE "http://localhost:8000/api/todos/1"
```

## Database Migrations

### Create a new migration

```bash
uv run alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
uv run alembic upgrade head
```

### Rollback migrations

```bash
uv run alembic downgrade -1
```

## Development

The application uses:

- **FastAPI** for the web framework
- **SQLAlchemy** for ORM
- **Pydantic** for data validation
- **Alembic** for database migrations
- **psycopg2-binary** for PostgreSQL driver
- **python-dotenv** for environment variable management

## License

MIT
