import pytest


@pytest.mark.asyncio
async def test_create_post(client, auth_headers):
    response = await client.post(
        "/api/posts",
        json={
            "title": "Test Post",
            "content": "Post content"
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Test Post"


@pytest.mark.asyncio
async def test_get_posts(client):
    response = await client.get("/api/posts")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_update_post(client, auth_headers):
    create = await client.post(
        "/api/posts",
        json={"title": "Old", "content": "Old content"},
        headers=auth_headers,
    )

    post_id = create.json()["id"]

    response = await client.put(
        f"/api/posts/{post_id}",
        json={"title": "New", "content": "New content"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New"


@pytest.mark.asyncio
async def test_update_post_forbidden(client, auth_headers):
    # First user creates post
    create = await client.post(
        "/api/posts",
        json={"title": "Secret", "content": "Hidden"},
        headers=auth_headers,
    )

    post_id = create.json()["id"]

    # Second user
    await client.post(
        "/api/users",
        json={
            "username": "other",
            "email": "other@example.com",
            "password": "password123"
        }
    )

    login = await client.post(
        "/api/users/token",
        data={
            "username": "other@example.com",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    headers2 = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = await client.put(
        f"/api/posts/{post_id}",
        json={"title": "Hack", "content": "Hack"},
        headers=headers2,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_post_forbidden(client, auth_headers):
    # First user creates a post
    create = await client.post(
        "/api/posts",
        json={"title": "Private", "content": "Secret"},
        headers=auth_headers,
    )

    post_id = create.json()["id"]

    # Create second user
    await client.post(
        "/api/users",
        json={
            "username": "other",
            "email": "other@example.com",
            "password": "password123"
        }
    )

    login = await client.post(
        "/api/users/token",
        data={
            "username": "other@example.com",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    headers2 = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # Second user attempts delete
    response = await client.delete(
        f"/api/posts/{post_id}",
        headers=headers2,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorised to delete this post"


@pytest.mark.asyncio
async def test_delete_post_not_found(client, auth_headers):
    response = await client.delete(
        "/api/posts/9999",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


@pytest.mark.asyncio
async def test_delete_post_success(client, auth_headers):
    # Create a post first
    create = await client.post(
        "/api/posts",
        json={"title": "To Delete", "content": "Delete me"},
        headers=auth_headers,
    )

    post_id = create.json()["id"]

    # Delete the post
    response = await client.delete(
        f"/api/posts/{post_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    # Confirm it no longer exists
    get_response = await client.get(f"/api/posts/{post_id}")
    assert get_response.status_code == 404