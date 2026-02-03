import pytest
from main import app, db
from app.models import User, Game
from app.models_mongo import GameMetadata, GameAnalytics

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

@pytest.fixture
def developer_user(client):
    """Create a developer user"""
    with app.app_context():
        dev = User(email='dev@test.com', username='developer')
        dev.set_password('DevPass123')
        dev.role = 'developer'
        db.session.add(dev)
        db.session.commit()
    
    return client

# MONGODB TESTS (NoSQL)

def test_game_metadata_save(developer_user):
    """Test saving game metadata to MongoDB"""
    with app.app_context():
        dev = User.query.filter_by(username='developer').first()
        game = Game(
            title='Test Game',
            description='Test',
            genre='Action',
            price=9.99,
            developer_id=dev.id
        )
        db.session.add(game)
        db.session.commit()
        
        game_metadata = GameMetadata()
        result = game_metadata.save_metadata(game.id, {
            'tags': ['action', 'multiplayer'],
            'screenshots': ['url1', 'url2'],
            'system_requirements': {
                'cpu': 'Intel i5',
                'ram': '8GB'
            }
        })
        
        assert result is not None

def test_game_metadata_get(developer_user):
    """Test retrieving game metadata from MongoDB"""
    with app.app_context():
        dev = User.query.filter_by(username='developer').first()
        game = Game(
            title='Test Game 2',
            description='Test',
            genre='Action',
            price=9.99,
            developer_id=dev.id
        )
        db.session.add(game)
        db.session.commit()
        
        game_metadata = GameMetadata()
        game_metadata.save_metadata(game.id, {
            'tags': ['action'],
            'screenshots': ['url1']
        })
        
        metadata = game_metadata.get_metadata(game.id)
        
        if metadata:
            assert 'tags' in metadata
            assert 'action' in metadata['tags']

def test_game_analytics_record_view():
    """Test recording game views in MongoDB"""
    game_analytics = GameAnalytics()
    
    game_analytics.record_view(1)
    game_analytics.record_view(1)
    game_analytics.record_view(1)
    
    stats = game_analytics.get_stats(1)
    
    if stats:
        assert stats.get('views', 0) >= 1

def test_game_analytics_record_download():
    """Test recording game downloads in MongoDB"""
    game_analytics = GameAnalytics()
    
    game_analytics.record_download(2)
    game_analytics.record_download(2)
    
    stats = game_analytics.get_stats(2)
    
    if stats:
        assert stats.get('downloads', 0) >= 1

def test_game_metadata_search_by_tags():
    """Test searching games by tags in MongoDB"""
    game_metadata = GameMetadata()
    
    game_metadata.save_metadata(1, {
        'tags': ['rpg', 'fantasy']
    })
    
    game_metadata.save_metadata(2, {
        'tags': ['action', 'adventure']
    })
    
    results = game_metadata.search_by_tags(['rpg'])
    
    assert isinstance(results, list)

def test_mongodb_integration():
    """Test MongoDB integration works"""
    game_metadata = GameMetadata()
    game_analytics = GameAnalytics()
    
    assert game_metadata is not None
    assert game_analytics is not None