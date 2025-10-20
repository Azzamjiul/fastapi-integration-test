"""
Todos API endpoint tests.

These tests verify the REST API endpoints for todo operations.
Uses centralized fixtures with feature-specific customizations.
"""
import pytest


def test_user_can_create_todo_and_get_the_todo(test_client, todo_data):
    """
    Test creating a todo via POST and retrieving it via GET.

    Demonstrates:
    - Using centralized test_client fixture
    - Using feature-specific todo_data factory fixture
    """
    # Create a new todo using the todo_data factory
    data = todo_data(
        title="Test Todo",
        description="This is a test todo",
        completed=False
    )

    # POST to create todo
    create_response = test_client.post("/api/todos/", json=data)
    assert create_response.status_code == 201
    created_todo = create_response.json()
    assert created_todo["title"] == data["title"]
    assert created_todo["description"] == data["description"]
    assert "id" in created_todo

    # GET the created todo
    todo_id = created_todo["id"]
    get_response = test_client.get(f"/api/todos/{todo_id}")
    assert get_response.status_code == 200
    retrieved_todo = get_response.json()
    assert retrieved_todo["id"] == todo_id
    assert retrieved_todo["title"] == data["title"]


def test_create_todo_with_defaults(test_client, todo_data):
    """
    Test creating todo using default values from todo_data factory.

    Demonstrates:
    - Using factory with default values
    - Feature-specific defaults are applied automatically
    """
    # Use factory without arguments - gets feature-specific defaults
    data = todo_data()

    response = test_client.post("/api/todos/", json=data)
    assert response.status_code == 201
    todo = response.json()
    assert todo["title"] == "Todos Feature Test"  # Default from conftest.py
    assert todo["completed"] is False


def test_update_todo(test_client, sample_todo):
    """
    Test updating an existing todo.

    Demonstrates:
    - Using feature-specific sample_todo fixture
    - Fixture provides pre-created todo for testing
    """
    todo_id = sample_todo["id"]

    # Update the todo
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True
    }
    response = test_client.put(f"/api/todos/{todo_id}", json=update_data)
    assert response.status_code == 200

    updated_todo = response.json()
    assert updated_todo["title"] == update_data["title"]
    assert updated_todo["completed"] is True


def test_delete_todo(test_client, sample_todo):
    """
    Test deleting a todo.

    Demonstrates:
    - Using sample_todo fixture for pre-created data
    - Verifying deletion via GET returning 404
    """
    todo_id = sample_todo["id"]

    # Delete the todo
    delete_response = test_client.delete(f"/api/todos/{todo_id}")
    assert delete_response.status_code == 204  # No Content

    # Verify it's deleted
    get_response = test_client.get(f"/api/todos/{todo_id}")
    assert get_response.status_code == 404


def test_list_todos(test_client, multiple_todos):
    """
    Test listing multiple todos.

    Demonstrates:
    - Using multiple_todos fixture for pre-created list
    - Testing list endpoints
    """
    response = test_client.get("/api/todos/")
    assert response.status_code == 200

    todos = response.json()
    assert len(todos) >= 5  # At least the 5 from fixture
    assert all("id" in todo for todo in todos)
    assert all("title" in todo for todo in todos)


@pytest.mark.parametrize("title,expected_status", [
    ("Valid Title", 201),
    ("A" * 200, 201),  # Long title
])
def test_create_todo_validation(test_client, todo_data, title, expected_status):
    """
    Test todo creation validation with various inputs.

    Demonstrates:
    - Parametrized testing
    - Testing validation rules
    """
    data = todo_data(title=title)
    response = test_client.post("/api/todos/", json=data)
    assert response.status_code == expected_status
