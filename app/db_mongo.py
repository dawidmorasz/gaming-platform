from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB_NAME = 'gaming_platform'

try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')
    mongo_db = mongo_client[MONGO_DB_NAME]
    print("✅ MongoDB connected!")
except ConnectionFailure:
    print("❌ MongoDB not connected - using local mode only")
    mongo_db = None
    mongo_client = None

def get_mongo_db():
    """Get MongoDB database instance"""
    return mongo_db