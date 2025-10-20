"""
Todos CRUD operations tests at the database level.

These tests verify CRUD operations work correctly at the database layer,
independent of the API layer.
"""
import pytest
from app.crud.todo import create_todo, get_todo, update_todo, delete_todo, get_todos
from app.schemas.todo import TodoCreate, TodoUpdate


def test_create_todo_crud(db, todo_data):
    """
    Test creating a todo directly via CRUD layer.

    Demonstrates:
    - Using db fixture for database session
    - Testing CRUD layer independently
    """
    data = todo_data()
    todo_create = TodoCreate(**data)

    todo = create_todo(db, todo_create)

    assert todo.id is not None
    assert todo.title == data["title"]
    assert todo.description == data["description"]
    assert todo.completed == data["completed"]


def test_get_todo_crud(db, todo_data):
    """Test retrieving a todo via CRUD layer."""
    # Create a todo first
    data = todo_data(title="CRUD Test Todo")
    todo_create = TodoCreate(**data)
    created_todo = create_todo(db, todo_create)

    # Retrieve it
    retrieved_todo = get_todo(db, created_todo.id)

    assert retrieved_todo is not None
    assert retrieved_todo.id == created_todo.id
    assert retrieved_todo.title == data["title"]


def test_update_todo_crud(db, todo_data):
    """Test updating a todo via CRUD layer."""
    # Create a todo first
    data = todo_data()
    todo_create = TodoCreate(**data)
    created_todo = create_todo(db, todo_create)

    # Update it
    update_data = TodoUpdate(title="Updated via CRUD", completed=True)
    updated_todo = update_todo(db, created_todo.id, update_data)

    assert updated_todo.title == "Updated via CRUD"
    assert updated_todo.completed is True


def test_delete_todo_crud(db, todo_data):
    """Test deleting a todo via CRUD layer."""
    # Create a todo first
    data = todo_data()
    todo_create = TodoCreate(**data)
    created_todo = create_todo(db, todo_create)

    # Delete it
    result = delete_todo(db, created_todo.id)
    assert result is True

    # Verify it's deleted
    deleted_todo = get_todo(db, created_todo.id)
    assert deleted_todo is None


def test_get_todos_crud(db, todo_data):
    """Test listing todos via CRUD layer."""
    # Create multiple todos
    for i in range(3):
        data = todo_data(title=f"CRUD List Test {i}")
        todo_create = TodoCreate(**data)
        create_todo(db, todo_create)

    # Get all todos
    todos = get_todos(db)

    assert len(todos) >= 3
    assert all(hasattr(todo, "id") for todo in todos)
    assert all(hasattr(todo, "title") for todo in todos)
