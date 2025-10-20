"""
Todos end-to-end workflow tests.

These tests verify complete user workflows that span multiple operations.
They test the full stack from API to database.
"""
import pytest


def test_complete_todo_lifecycle(test_client, todo_data):
    """
    Test complete lifecycle: Create -> Read -> Update -> Complete -> Delete.

    Demonstrates:
    - End-to-end workflow testing
    - Testing multiple operations in sequence
    - Real-world usage patterns
    """
    # 1. Create a todo
    data = todo_data(title="Lifecycle Test Todo", completed=False)
    create_response = test_client.post("/api/todos/", json=data)
    assert create_response.status_code == 201
    todo = create_response.json()
    todo_id = todo["id"]

    # 2. Read the todo
    get_response = test_client.get(f"/api/todos/{todo_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == data["title"]

    # 3. Update the todo
    update_data = {"title": "Updated Lifecycle Todo", "description": data["description"], "completed": False}
    update_response = test_client.put(f"/api/todos/{todo_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Lifecycle Todo"

    # 4. Mark as complete
    complete_data = {"title": update_data["title"], "description": data["description"], "completed": True}
    complete_response = test_client.put(f"/api/todos/{todo_id}", json=complete_data)
    assert complete_response.status_code == 200
    assert complete_response.json()["completed"] is True

    # 5. Delete the todo
    delete_response = test_client.delete(f"/api/todos/{todo_id}")
    assert delete_response.status_code == 204  # No Content

    # 6. Verify deletion
    final_get = test_client.get(f"/api/todos/{todo_id}")
    assert final_get.status_code == 404


def test_batch_todo_operations(test_client, todo_data):
    """
    Test batch operations: Create multiple, update some, delete others.

    Demonstrates:
    - Batch operations
    - Complex workflows
    """
    # Create 5 todos
    todo_ids = []
    for i in range(5):
        data = todo_data(title=f"Batch Todo {i}")
        response = test_client.post("/api/todos/", json=data)
        assert response.status_code == 201
        todo_ids.append(response.json()["id"])

    # Update first 2 todos
    for i in range(2):
        update_data = {
            "title": f"Updated Batch Todo {i}",
            "description": "Updated",
            "completed": True
        }
        response = test_client.put(f"/api/todos/{todo_ids[i]}", json=update_data)
        assert response.status_code == 200

    # Delete last 2 todos
    for i in range(3, 5):
        response = test_client.delete(f"/api/todos/{todo_ids[i]}")
        assert response.status_code == 204  # No Content

    # Verify: Should have 3 todos remaining
    # (IDs 0, 1, 2 - where 0 and 1 are completed, 2 is not)
    for i in range(3):
        response = test_client.get(f"/api/todos/{todo_ids[i]}")
        assert response.status_code == 200

    # Verify deleted todos
    for i in range(3, 5):
        response = test_client.get(f"/api/todos/{todo_ids[i]}")
        assert response.status_code == 404


@pytest.mark.slow
def test_large_dataset_handling(test_client, todo_data):
    """
    Test handling large number of todos.

    Demonstrates:
    - Performance testing
    - Using @pytest.mark.slow for long-running tests
    """
    # Create 50 todos
    for i in range(50):
        data = todo_data(title=f"Large Dataset Todo {i}")
        response = test_client.post("/api/todos/", json=data)
        assert response.status_code == 201

    # List all todos
    response = test_client.get("/api/todos/")
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) >= 50
