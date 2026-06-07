"""Todo tests."""

import pytest
from httpx import AsyncClient


async def get_auth_token(client: AsyncClient, email: str = "todo@example.com") -> str:
    """Helper to register and get auth token."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_todo(client: AsyncClient):
    """Test creating a new todo."""
    token = await get_auth_token(client, "create@example.com")

    response = await client.post(
        "/api/v1/todos",
        json={"title": "Test Todo", "description": "A test todo item"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "A test todo item"
    assert data["completed"] is False


@pytest.mark.asyncio
async def test_get_todos(client: AsyncClient):
    """Test getting todo list."""
    token = await get_auth_token(client, "list@example.com")

    # Create a todo first
    await client.post(
        "/api/v1/todos",
        json={"title": "List Todo"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Get todos
    response = await client.get(
        "/api/v1/todos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_todo_list_cache_is_invalidated_after_create(client: AsyncClient):
    """Creating a todo should invalidate the cached todo list for that user."""
    token = await get_auth_token(client, "cache@example.com")

    first_create = await client.post(
        "/api/v1/todos",
        json={"title": "Cached Todo 1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert first_create.status_code == 201

    first_list = await client.get(
        "/api/v1/todos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert first_list.status_code == 200
    assert first_list.json()["total"] == 1

    second_create = await client.post(
        "/api/v1/todos",
        json={"title": "Cached Todo 2"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert second_create.status_code == 201

    second_list = await client.get(
        "/api/v1/todos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert second_list.status_code == 200
    assert second_list.json()["total"] == 2


@pytest.mark.asyncio
async def test_update_todo(client: AsyncClient):
    """Test updating a todo."""
    token = await get_auth_token(client, "update@example.com")

    # Create a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Update Me"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    # Update it
    response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"title": "Updated Title", "completed": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_partial_update_preserves_description_and_allows_completed_false(
    client: AsyncClient,
):
    """Partial updates should preserve omitted fields and allow completed=False."""
    token = await get_auth_token(client, "partial@example.com")

    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Partial Todo", "description": "Keep this description"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    response_true = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"completed": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_true.status_code == 200
    assert response_true.json()["completed"] is True

    response_false = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"completed": False, "title": "Partial Todo Updated"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_false.status_code == 200
    data = response_false.json()
    assert data["completed"] is False
    assert data["title"] == "Partial Todo Updated"
    assert data["description"] == "Keep this description"


@pytest.mark.asyncio
async def test_delete_todo(client: AsyncClient):
    """Test deleting a todo."""
    token = await get_auth_token(client, "delete@example.com")

    # Create a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Delete Me"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    # Delete it
    response = await client.delete(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_single_todo(client: AsyncClient):
    """Test getting a single todo by ID."""
    token = await get_auth_token(client, "single@example.com")

    # Create a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Single Todo", "description": "Get me"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    # Get it
    response = await client.get(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Single Todo"
