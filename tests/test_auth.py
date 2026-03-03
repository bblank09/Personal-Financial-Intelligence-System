import json

def test_register(client):
    response = client.post('/api/register', 
        data=json.dumps({"username": "testuser", "email": "test@example.com", "password": "password123"}),
        content_type='application/json'
    )
    assert response.status_code == 201
    assert b"User registered successfully" in response.data

def test_login(client):
    # Setup user
    client.post('/api/register', 
        data=json.dumps({"username": "testuser", "email": "test@example.com", "password": "password123"}),
        content_type='application/json'
    )
    
    # Test valid login
    response = client.post('/api/login', 
        data=json.dumps({"email": "test@example.com", "password": "password123"}),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert b"Login successful" in response.data

def test_invalid_login(client):
    response = client.post('/api/login', 
        data=json.dumps({"email": "wrong@example.com", "password": "password123"}),
        content_type='application/json'
    )
    assert response.status_code == 401
