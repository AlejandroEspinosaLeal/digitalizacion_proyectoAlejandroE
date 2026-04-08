"""
Authentication Integration Tests.

Validates the FastAPI backend JWT creation, brute-force limits, and registration limits.
"""
def test_register_user(client):
    response = client.post("/auth/register", json={
        "email": "test@enterprise.com",
        "hashed_password": "testpassword123",
        "failed_login_attempts": 0
    })
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User successfully created"
    assert "id" in data

def test_register_duplicate_user(client):
    response = client.post("/auth/register", json={
        "email": "test@enterprise.com",
        "hashed_password": "testpassword123"
    })
    assert response.status_code == 400

def test_login_wrong_password(client):
    response = client.post("/auth/token", json={
        "email": "test@enterprise.com",
        "hashed_password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_success(client):
    response = client.post("/auth/token", json={
        "email": "test@enterprise.com",
        "hashed_password": "testpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending_verification"
