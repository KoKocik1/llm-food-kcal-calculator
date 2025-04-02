from model.meal import Meal
from typing import List


def collection_to_meal(collection: dict) -> Meal:
    """Convert a MongoDB document to a Meal object.

    Args:
        collection (dict): MongoDB document representing a meal

    Returns:
        Meal: Converted Meal object
    """
    meal_dict = collection.copy()
    meal = Meal(**meal_dict)
    return meal


def collections_to_meals(collections: List[dict]) -> List[Meal]:
    """Convert multiple MongoDB documents to Meal objects.

    Args:
        collections (List[dict]): List of MongoDB documents

    Returns:
        List[Meal]: List of converted Meal objects
    """
    return [collection_to_meal(collection) for collection in collections]
