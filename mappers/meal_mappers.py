from model.meal import Meal
from typing import List
from tabulate import tabulate


def collection_to_meal(collection: dict) -> Meal:
    """Convert a MongoDB document to a Meal object."""
    meal_dict = collection.copy()
    meal = Meal(**meal_dict)
    return meal


def collections_to_meals(collections: List[dict]) -> List[Meal]:
    """Convert multiple MongoDB documents to Meal objects"""
    return [collection_to_meal(collection) for collection in collections]


def print_meals(meals: List[Meal]):
    """Print a list of Meal objects"""
    if meals:
        # Convert Meal objects to dictionaries
        meals_dict = [meal.to_dict() for meal in meals]
        print(tabulate(meals_dict, headers="keys", tablefmt="grid"))
    else:
        print("No meals found")


def print_meal(meal: Meal):
    """Print a single Meal object"""
    print(tabulate([meal.to_dict()], headers="keys", tablefmt="grid"))
