from app.db_mongo import get_mongo_db
from datetime import datetime

class GameMetadata:
    """Store game metadata in MongoDB"""
    
    def __init__(self):
        self.db = get_mongo_db()
        if self.db is not None:
            self.collection = self.db['game_metadata']
        else:
            self.collection = None
    
    def save_metadata(self, game_id, metadata):
        """Save game metadata to MongoDB"""
        if self.db is None:
            return None
        
        doc = {
            'game_id': game_id,
            'tags': metadata.get('tags', []),
            'screenshots': metadata.get('screenshots', []),
            'videos': metadata.get('videos', []),
            'system_requirements': metadata.get('system_requirements', {}),
            'developer_notes': metadata.get('developer_notes', ''),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.update_one(
            {'game_id': game_id},
            {'$set': doc},
            upsert=True
        )
        return result.upserted_id or result.modified_count
    
    def get_metadata(self, game_id):
        """Get game metadata from MongoDB"""
        if self.db is None:
            return None
        
        return self.collection.find_one({'game_id': game_id})
    
    def search_by_tags(self, tags):
        """Search games by tags"""
        if self.db is None:
            return []
        
        return list(self.collection.find({'tags': {'$in': tags}}))

class GameAnalytics:
    """Store game analytics in MongoDB"""
    
    def __init__(self):
        self.db = get_mongo_db()
        if self.db is not None:
            self.collection = self.db['game_analytics']
        else:
            self.collection = None
    
    def record_view(self, game_id):
        """Record a game view"""
        if self.db is None:
            return
        
        self.collection.update_one(
            {'game_id': game_id},
            {'$inc': {'views': 1}},
            upsert=True
        )
    
    def record_download(self, game_id):
        """Record a game download"""
        if self.db is None:
            return
        
        self.collection.update_one(
            {'game_id': game_id},
            {'$inc': {'downloads': 1}},
            upsert=True
        )
    
    def get_stats(self, game_id):
        """Get game statistics"""
        if self.db is None:
            return {'views': 0, 'downloads': 0}
        
        return self.collection.find_one({'game_id': game_id})