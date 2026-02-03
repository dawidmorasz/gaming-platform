from main import app
import json

client = app.test_client()

print("=" * 50)
print("TESTING AUTHENTICATION")
print("=" * 50)

print("\n1. Testing Registration...")
response = client.post('/auth/register', 
    json={
        'email': 'user@example.com',
        'username': 'player1',
        'password': 'Password123'
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

print("\n2. Testing duplicate username (should fail)...")
response = client.post('/auth/register',
    json={
        'email': 'another@example.com',
        'username': 'player1',
        'password': 'Password123'
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

print("\n3. Testing Login (correct password)...")
response = client.post('/auth/login',
    json={
        'email_or_username': 'player1',
        'password': 'Password123'
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

print("\n4. Testing Login (wrong password - should fail)...")
response = client.post('/auth/login',
    json={
        'email_or_username': 'player1',
        'password': 'WrongPassword'
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

print("\n" + "=" * 50)
print("All tests complete!")
print("=" * 50)