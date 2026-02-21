import pytest


# ---------------------------------------------------
# Helper function to create a user and return auth header
# ---------------------------------------------------
async def create_user_and_token(client):
    # Create a user
    await client.post(
        "/api/users",
        json={
            "username": "postuser",
            "email": "post@example.com",
            "password": "password123"
        }
    )

    # Log in to get JWT token
    login = await client.post(
        "/api/users/token",
        data={
            "username": "post@example.com",  # using email as username field
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Extract token from response
    token = login.json()["access_token"]

    # Return Authorization header
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------
# Test creating a post (authenticated)
# ---------------------------------------------------
@pytest.mark.asyncio
async def test_create_post(client):
    # Get authentication headers
    headers = await create_user_and_token(client)

    # Create a new post
    response = await client.post(
        "/api/posts",
        json={
            "title": "Test Post",
            "content": "Post content"
        },
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Test Post"


# ---------------------------------------------------
# Test retrieving posts (public route)
# ---------------------------------------------------
@pytest.mark.asyncio
async def test_get_posts(client):
    response = await client.get("/api/posts")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------
# Test updating your own post
# ---------------------------------------------------
@pytest.mark.asyncio
async def test_update_post(client):
    headers = await create_user_and_token(client)

    # Create post first
    create = await client.post(
        "/api/posts",
        json={"title": "Old", "content": "Old content"},
        headers=headers,
    )

    post_id = create.json()["id"]

    # Update the post
    response = await client.put(
        f"/api/posts/{post_id}",
        json={"title": "New", "content": "New content"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New"


# ---------------------------------------------------
# Test updating someone else's post (should fail)
# ---------------------------------------------------
@pytest.mark.asyncio
async def test_update_post_forbidden(client):
    # First user creates a post
    headers1 = await create_user_and_token(client)

    create = await client.post(
        "/api/posts",
        json={"title": "Secret", "content": "Hidden"},
        headers=headers1,
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

    # Login second user
    login = await client.post(
        "/api/users/token",
        data={
            "username": "other@example.com",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    headers2 = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # Second user attempts to update first user's post
    response = await client.put(
        f"/api/posts/{post_id}",
        json={"title": "Hack", "content": "Hack"},
        headers=headers2,
    )

    # Should be forbidden
    assert response.status_code == 403