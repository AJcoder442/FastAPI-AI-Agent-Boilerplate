def test_register_user(client):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "strongpassword123"
    }
    response = client.post("/users/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data

def test_register_duplicate_email(client):
    payload = {
        "username": "user1",
        "email": "dup@example.com",
        "password": "password123"
    }
    # Register first time
    response = client.post("/users/register", json=payload)
    assert response.status_code == 201
    
    # Register second time with duplicate email
    payload["username"] = "user2"
    response = client.post("/users/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exits "

def test_login_user(client):
    # Register
    payload = {
        "username": "loginuser",
        "email": "loginuser@example.com",
        "password": "password123"
    }
    client.post("/users/register", json=payload)
    
    # Login
    response = client.post("/users/login", data={"username": payload["email"], "password": payload["password"]})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    response = client.post("/users/login", data={"username": "wrong@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_get_current_user_profile(client, auth_headers):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

def test_update_profile(client, auth_headers):
    payload = {
        "username": "updatedtestuser",
        "email": "updatedtestuser@example.com"
    }
    response = client.put("/users/me", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updatedtestuser"
    assert data["email"] == "updatedtestuser@example.com"

def test_change_password(client, auth_headers):
    # Change password
    payload = {
        "old_password": "testpassword123",
        "new_password": "newpassword123"
    }
    response = client.put("/users/me/change-password", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"
    
    # Verify login with new password
    response_login = client.post("/users/login", data={"username": "testuser@example.com", "password": "newpassword123"})
    assert response_login.status_code == 200
    assert "access_token" in response_login.json()

def test_refresh_token_and_logout(client):
    # Register and login
    payload = {
        "username": "refreshuser",
        "email": "refresh@example.com",
        "password": "password123"
    }
    client.post("/users/register", json=payload)
    res_login = client.post("/users/login", data={"username": payload["email"], "password": payload["password"]})
    assert res_login.status_code == 200
    rt = res_login.json()["refresh_token"]
    
    # Refresh
    res_refresh = client.post("/users/refresh", json={"refresh_token": rt})
    assert res_refresh.status_code == 200
    data_refresh = res_refresh.json()
    assert "access_token" in data_refresh
    assert "refresh_token" in data_refresh
    rotated_rt = data_refresh["refresh_token"]
    
    # Logout
    res_logout = client.post("/users/logout", json={"refresh_token": rotated_rt})
    assert res_logout.status_code == 200
    assert res_logout.json()["message"] == "Logged out successfully"
    
    # Verify rotated token is now invalid
    res_invalid_refresh = client.post("/users/refresh", json={"refresh_token": rotated_rt})
    assert res_invalid_refresh.status_code == 401
