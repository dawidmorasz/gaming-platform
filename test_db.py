from main import app, db
from app.models import User, Game

with app.app_context():
    user = User(
        email='player@test.com',
        username='testplayer',
        display_name='Test Player',
        role='player'
    )
    user.set_password('Password123')

    db.session.add(user)
    db.session.commit()

    print("User created successfully!")
    print(f"User ID: {user.id}")
    print(f"Username: {user.username}")

    game = Game(
        title='Test Game',
        description='A test game',
        genre='Adventure',
        price=9.99,
        developer_id=user.id
    )

    db.session.add(game)
    db.session.commit()

    print("Game created successfully!")
    print(f"Game: {game.title}")
    print(f"Price: ${game.price}")

    all_users = User.query.all()
    print(f"\n✅ Total users in database: {len(all_users)}")
    
    all_games = Game.query.all()
    print(f"✅ Total games in database: {len(all_games)}")