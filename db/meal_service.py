import streamlit as st
from db.mongo import get_mongo_db
import os
from model.meal import Meal
from model.mealCreate import MealCreate
from datetime import datetime
from typing import List
from mappers.meal_mappers import collections_to_meals
from tabulate import tabulate


def get_meals_from_date_range(
    start_date: datetime, end_date: datetime = datetime.now()
) -> List[Meal]:
    """Get all meals from a given date onwards.

    Args:
        date (datetime): Starting date to get meals from

    Returns:
        List[Meal]: List of meals after the given date
    """
    db = get_mongo_db()
    collection_meals = db[os.getenv("MONGO_COLLECTION_MEALS")]
    start_of_day = datetime(start_date.year, start_date.month, start_date.day)
    end_of_day = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
    collections = collection_meals.find(
        {"date": {"$gte": start_of_day, "$lte": end_of_day}}
    )
    return collections_to_meals(collections)


def get_meal_by_day(date: datetime) -> List[Meal]:
    """Get all meals for a specific day.

    Args:
        date (datetime): Date to get meals for

    Returns:
        List[Meal]: List of meals for that day
    """
    start_of_day = datetime(date.year, date.month, date.day)
    end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)

    return get_meals_from_date_range(start_of_day, end_of_day)


def create_meal(meal: MealCreate) -> None:
    """Create a new meal in the database.

    Args:
        meal (Meal): Meal object to create
    """
    db = get_mongo_db()
    collection_meals = db[os.getenv("MONGO_COLLECTION_MEALS")]
    meal_dict = meal.to_dict()
    collection_meals.insert_one(meal_dict)
    print(f"Created meal: {meal_dict}")


def edit_meal(id: str, meal: MealCreate) -> None:
    """Edit an existing meal in the database.

    Args:
        id (str): MongoDB _id of meal to edit
        meal (Meal): Updated meal object
    """
    db = get_mongo_db()
    collection_meals = db[os.getenv("MONGO_COLLECTION_MEALS")]
    collection_meals.update_one({"_id": id}, {"$set": meal.to_dict()})


def delete_meal(id: str) -> None:
    """Delete a meal from the database.

    Args:
        id (str): MongoDB _id of meal to delete
    """
    db = get_mongo_db()
    collection_meals = db[os.getenv("MONGO_COLLECTION_MEALS")]
    collection_meals.delete_one({"_id": id})


if __name__ == "__main__":

    print("========== Create Meal ==========")
    create_meal(
        MealCreate(
            name="Test Meal1",
            calories=100,
            category="Lunch",
            date=datetime.now(),
            description="Test Description1",
        )
    )
    meals = get_meal_by_day(datetime.now())
    created_meal = list(filter(lambda x: x.name == "Test Meal1", meals))
    created_meal_id = created_meal[0]._id
    print(tabulate([meal.to_dict() for meal in meals], headers="keys", tablefmt="grid"))

    print("========== Edit Meal ==========")
    edit_meal(
        created_meal_id,
        MealCreate(
            name="Updated Meal1",
            calories=200,
            category="Lunch",
            date=datetime.now(),
            description="Updated Description1",
        ),
    )
    meals = get_meal_by_day(datetime.now())
    print(tabulate([meal.to_dict() for meal in meals], headers="keys", tablefmt="grid"))

    print("========== Delete Meal ==========")
    delete_meal(created_meal_id)
    meals = get_meal_by_day(datetime.now())
    print(tabulate([meal.to_dict() for meal in meals], headers="keys", tablefmt="grid"))
