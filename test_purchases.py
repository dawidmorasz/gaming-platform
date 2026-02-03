from main import app
from app.models import db, User, Game, Order

client = app.test_client()

print("=" * 50)
print("TESTING PURCHASES API")
print("=" * 50)

with app.app_context():
    player = User.query.filter_by(username='player').first()
    if not player:
        player = User(
            email='player@example.com',
            username='player',
            role='player'
        )
        player.set_password('Password123')
        db.session.add(player)
        db.session.commit()
        print("✅ Player user created")
    
    game = Game.query.first()
    if not game:
        dev = User.query.filter_by(role='developer').first()
        game = Game(
            title='Test Game',
            description='A test game',
            genre='RPG',
            price=9.99,
            developer_id=dev.id if dev else 1
        )
        db.session.add(game)
        db.session.commit()
        print(f"✅ Game created: {game.title}")
        game_id = game.id
    else:
        game_id = game.id
        print(f"✅ Using existing game: {game.title}")

print("\n1. Logging in as player...")
response = client.post('/auth/login',
    json={
        'email_or_username': 'player',
        'password': 'Password123'
    }
)
print(f"Status: {response.status_code}")

print(f"\n2. Buying game {game_id}...")
response = client.post('/api/purchases/checkout',
    json={'game_id': game_id}
)
print(f"Status: {response.status_code}")
data = response.get_json()
print(f"Response: {data}")

print(f"\n3. Buying same game again (should fail)...")
response = client.post('/api/purchases/checkout',
    json={'game_id': game_id}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

print("\n4. Getting purchase history...")
response = client.get('/api/purchases/history')
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

print("\n5. Getting library...")
response = client.get('/api/purchases/library')
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

print("\n" + "=" * 50)
print("✅ Purchases tests complete!")
print("=" * 50)