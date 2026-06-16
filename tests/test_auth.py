"""
Test authentication endpoints
"""

import json

def test_register(client):
    """Test user registration"""
    response = client.post(
        '/api/auth/register',
        data=json.dumps({
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@test.com',
            'password': 'password123',
            'role_name': 'student'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    assert response.json['success'] is True

def test_register_duplicate_email(client):
    """Test registration with duplicate email"""
    email = 'duplicate@test.com'
    
    # First registration
    client.post(
        '/api/auth/register',
        data=json.dumps({
            'first_name': 'Test',
            'last_name': 'User',
            'email': email,
            'password': 'password123',
            'role_name': 'student'
        }),
        content_type='application/json'
    )
    
    # Second registration with same email
    response = client.post(
        '/api/auth/register',
        data=json.dumps({
            'first_name': 'Test2',
            'last_name': 'User2',
            'email': email,
            'password': 'password123',
            'role_name': 'student'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400

def test_login(client, init_database):
    """Test user login"""
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'email': 'admin@test.com',
            'password': 'admin123'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'access_token' in response.json['data']

def test_login_invalid_password(client, init_database):
    """Test login with invalid password"""
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'email': 'admin@test.com',
            'password': 'wrongpassword'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 401

def test_get_current_user(client, init_database):
    """Test getting current user"""
    # Login first
    login_response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'email': 'admin@test.com',
            'password': 'admin123'
        }),
        content_type='application/json'
    )
    
    token = login_response.json['data']['access_token']
    
    # Get current user
    response = client.get(
        '/api/auth/me',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['data']['email'] == 'admin@test.com'

def test_change_password(client, init_database):
    """Test changing password"""
    # Login first
    login_response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'email': 'admin@test.com',
            'password': 'admin123'
        }),
        content_type='application/json'
    )
    
    token = login_response.json['data']['access_token']
    
    # Change password
    response = client.post(
        '/api/auth/change-password',
        data=json.dumps({
            'old_password': 'admin123',
            'new_password': 'newpassword123'
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    
    # Try logging in with new password
    login_response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'email': 'admin@test.com',
            'password': 'newpassword123'
        }),
        content_type='application/json'
    )
    
    assert login_response.status_code == 200
