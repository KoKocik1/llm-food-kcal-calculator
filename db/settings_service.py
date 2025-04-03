from db.mongo import get_mongo_db
import os
from typing import List


def get_user_settings() -> List[str]:
    """Get all settings from the database"""
    db = get_mongo_db()
    collection_settings = db[os.getenv("MONGO_COLLECTION_SETTINGS")]
    collections = collection_settings.find()
    settings = collections[0]
    return settings


def update_user_settings(settings: dict) -> bool:
    """Update user settings in the database"""
    db = get_mongo_db()
    collection_settings = db[os.getenv("MONGO_COLLECTION_SETTINGS")]
    result = collection_settings.update_one({}, {"$set": settings})
    return result.modified_count > 0


def set_sample_settings() -> None:
    """Initialize sample settings if none exist."""
    db = get_mongo_db()
    collection_settings = db[os.getenv("MONGO_COLLECTION_SETTINGS")]
    if collection_settings.count_documents({}) == 0:
        default_settings = {
            "sex": "Male",
            "age": 40,
            "height": 170,
            "weight": 70,
            "target_calories": 2000
        }
        collection_settings.insert_one(default_settings)
    else:
        print("Settings already set")


if __name__ == "__main__":
    set_sample_settings()
    print(get_user_settings())
