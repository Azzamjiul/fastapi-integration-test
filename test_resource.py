def test_create_and_get_todo(test_client):
    # Create a new todo
    todo_data = {
        "title": "Test Todo",
        "description": "This is a test todo",
        "completed": False
    }
    create_response = test_client.post("/api/todos/", json=todo_data)
    assert create_response.status_code == 201
    created_todo = create_response.json()
    assert created_todo["title"] == todo_data["title"]
    assert created_todo["description"] == todo_data["description"]
    assert "id" in created_todo

    # Get the created todo
    todo_id = created_todo["id"]
    get_response = test_client.get(f"/api/todos/{todo_id}")
    assert get_response.status_code == 200
    retrieved_todo = get_response.json()
    assert retrieved_todo["id"] == todo_id
    assert retrieved_todo["title"] == todo_data["title"]
