from main import app
from app.models import db, User, Game

client = app.test_client()

print("=" * 50)
print("TESTING GAMES API")
print("=" * 50)

with app.app_context():
    dev = User.query.filter_by(username='developer1').first()
    if not dev:
        dev = User(
            email='dev@example.com',
            username='developer1',
            role='developer'
        )
        dev.set_password('Password123')
        db.session.add(dev)
        db.session.commit()
        print("✅ Developer user created")

print("\n1. Creating game without login (should fail)...")
response = client.post('/api/games',
    json={
        'title': 'My Game',
        'description': 'A cool game',
        'genre': 'RPG',
        'price': 19.99
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

print("\n2. Logging in as developer...")
response = client.post('/auth/login',
    json={
        'email_or_username': 'developer1',
        'password': 'Password123'
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

print("\n3. Getting all games...")
response = client.get('/api/games')
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

print("\n4. Creating game with login...")
response = client.post('/api/games',
    json={
        'title': 'Awesome RPG',
        'description': 'An amazing RPG game',
        'genre': 'RPG',
        'price': 29.99
    }
)
print(f"Status: {response.status_code}")
data = response.get_json()
print(f"Response: {data}")
game_id = data.get('id')

if game_id:
    print(f"\n5. Getting game {game_id}...")
    response = client.get(f'/api/games/{game_id}')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")

print("\n6. Searching for 'RPG'...")
response = client.get('/api/games/search?q=RPG')
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

print("\n" + "=" * 50)
print("✅ Games API tests complete!")
print("=" * 50)