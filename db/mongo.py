from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()


def get_mongo_client():
    """Connect to MongoDB and return the client."""
    client = MongoClient(os.getenv("MONGO_URI"))
    return client


def get_mongo_db():
    """Connect to MongoDB and return the database."""
    client = get_mongo_client()
    db_name = os.getenv("MONGO_DB_NAME")
    if db_name not in client.list_database_names():
        db = client[db_name]
        # Create initial collections
        db.create_collection(os.getenv("MONGO_COLLECTION_MEALS"))
        db.create_collection(os.getenv("MONGO_COLLECTION_CATEGORIES"))
    db = client[db_name]
    return db
