from db.mongo import get_mongo_db
import os
from typing import List


def get_categories() -> List[str]:
    """Get all meal categories from the database.

    Returns:
        List[str]: List of category names
    """
    db = get_mongo_db()
    collection_categories = db[os.getenv("MONGO_COLLECTION_CATEGORIES")]
    collections = collection_categories.find()
    return [category["name"] for category in collections]


def set_sample_categories() -> None:
    """Initialize sample meal categories if none exist."""
    db = get_mongo_db()
    collection_categories = db[os.getenv("MONGO_COLLECTION_CATEGORIES")]
    if collection_categories.count_documents({}) == 0:
        default_categories = [
            {"name": "Breakfast"},
            {"name": "Brunch"},
            {"name": "Lunch"},
            {"name": "Dinner"},
            {"name": "Snack"},
        ]
        collection_categories.insert_many(default_categories)
    else:
        print("Categories already set")


if __name__ == "__main__":
    set_sample_categories()
    print(get_categories())
