import pytest
from main import app, db
from app.models import User, Game, Review, Order

@pytest.fixture
def client():
    """Create test client with in-memory database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

# DATABASE TESTS (SQL)

def test_user_creation(client):
    """Test creating a user in SQL database"""
    with app.app_context():
        user = User(
            email='testuser@test.com',
            username='testuser123',
            display_name='Test User'
        )
        user.set_password('TestPassword123')
        
        db.session.add(user)
        db.session.commit()
        
        retrieved_user = User.query.filter_by(username='testuser123').first()
        assert retrieved_user is not None
        assert retrieved_user.email == 'testuser@test.com'

def test_user_password_hashing(client):
    """Test that passwords are hashed"""
    with app.app_context():
        user = User(
            email='hashtest@test.com',
            username='hashtest456'
        )
        user.set_password('MyPassword123')
        
        db.session.add(user)
        db.session.commit()
        
        assert user.password_hash != 'MyPassword123'
        assert user.check_password('MyPassword123')

def test_game_creation(client):
    """Test creating a game in SQL database"""
    with app.app_context():
        user = User(
            email='dev@test.com',
            username='developer789'
        )
        user.set_password('DevPass123')
        user.role = 'developer'
        db.session.add(user)
        db.session.commit()
        
        game = Game(
            title='Test Game SQL',
            description='A test game',
            genre='Action',
            price=9.99,
            developer_id=user.id
        )
        db.session.add(game)
        db.session.commit()
        
        retrieved_game = Game.query.filter_by(title='Test Game SQL').first()
        assert retrieved_game is not None
        assert retrieved_game.developer_id == user.id

def test_review_creation(client):
    """Test creating a review in SQL database"""
    with app.app_context():
        dev = User(email='dev2@test.com', username='dev2')
        dev.set_password('Pass123')
        dev.role = 'developer'
        db.session.add(dev)
        
        player = User(email='player2@test.com', username='player2')
        player.set_password('Pass123')
        db.session.add(player)
        db.session.commit()
        
        game = Game(
            title='Game2',
            description='Test',
            genre='Action',
            price=9.99,
            developer_id=dev.id
        )
        db.session.add(game)
        db.session.commit()
        
        review = Review(
            user_id=player.id,
            game_id=game.id,
            rating=5,
            title='Great Game!',
            content='Really enjoyed this game'
        )
        db.session.add(review)
        db.session.commit()
        
        retrieved_review = Review.query.first()
        assert retrieved_review is not None
        assert retrieved_review.rating == 5

def test_game_exists_in_database(client):
    """Test that games can be queried from database"""
    with app.app_context():
        dev = User(email='dev5@test.com', username='dev5')
        dev.set_password('Pass123')
        dev.role = 'developer'
        db.session.add(dev)
        db.session.commit()
        
        game = Game(
            title='TestGame5',
            description='Test',
            genre='Action',
            price=9.99,
            developer_id=dev.id
        )
        db.session.add(game)
        db.session.commit()
        
        retrieved = Game.query.get(game.id)
        assert retrieved is not None
        assert retrieved.title == 'TestGame5'

def test_user_role_assignment(client):
    """Test assigning different roles to users"""
    with app.app_context():
        user = User(
            email='role@test.com',
            username='roletest'
        )
        user.set_password('Pass123')
        user.role = 'admin'
        
        db.session.add(user)
        db.session.commit()
        
        retrieved = User.query.filter_by(username='roletest').first()
        assert retrieved.role == 'admin'

def test_game_price_storage(client):
    """Test that game prices are stored correctly"""
    with app.app_context():
        dev = User(email='dev6@test.com', username='dev6')
        dev.set_password('Pass123')
        dev.role = 'developer'
        db.session.add(dev)
        db.session.commit()
        
        game = Game(
            title='Game6',
            description='Test',
            genre='Action',
            price=29.99,
            developer_id=dev.id
        )
        db.session.add(game)
        db.session.commit()
        
        retrieved = Game.query.filter_by(title='Game6').first()
        assert retrieved.price == 29.99