import streamlit as st
from db.mongo import get_mongo_db
import os
from model.meal import Meal
from model.mealCreate import MealCreate
from datetime import datetime
from typing import List, Dict, Any, Optional
from mappers.meal_mappers import collections_to_meals
from tabulate import tabulate
from langchain.tools import tool
from bson import ObjectId


@tool
def get_meals_by_date_range(start_date: str, end_date: str = None) -> List[Meal]:
    """Get all meals from a given date onwards.

    Args:
        date (datetime): Starting date to get meals from

    Returns:
        List[Meal]: List of meals after the given date
    """
    db = get_mongo_db()
    collection_meals = db[os.getenv("MONGO_COLLECTION_MEALS")]
    start_date = datetime.strptime(start_date, "%Y-%m-%d")

    if end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    else:
        end_date = start_date

    start_of_day = datetime(start_date.year, start_date.month, start_date.day)
    end_of_day = datetime(end_date.year, end_date.month,
                          end_date.day, 23, 59, 59)
    collections = collection_meals.find(
        {"date": {"$gte": start_of_day, "$lte": end_of_day}}
    )
    return collections_to_meals(collections)


@tool
def get_meals_by_day(date: str = datetime.now().strftime("%Y-%m-%d")) -> List[Meal]:
    """Get all meals for a specific day. If no date is provided, it defaults to today.
    The date is formatted as YYYY-MM-DD. 

    Args:
        date (str): Date to get meals for (default is today)

    Returns:
        List[Meal]: List of meals for that day
    """
    return get_meals_by_date_range(date)


@tool
def get_meal_by_id(id: str) -> Optional[Meal]:
    """Get a meal by its id.

    Args:
        id (str): Id of the meal to get

    Returns:
        Optional[Meal]: Meal object
    """
    db = get_mongo_db()
    collection_meals = db[os.getenv("MONGO_COLLECTION_MEALS")]
    meal = collection_meals.find_one({"_id": id})
    if meal:
        return Meal(**meal)
    return None


@tool
def create_meal(meal: MealCreate) -> Dict[str, Any]:
    """Create a new meal in the database.

    Args:
        meal (MealCreate): Meal object to create

    Returns:
        Dict[str, Any]: Meal object with _id
    """
    db = get_mongo_db()
    collection_meals = db[os.getenv("MONGO_COLLECTION_MEALS")]

    meal_dict = meal.dict()
    meal_dict["date"] = datetime.strptime(meal_dict["date"], "%Y-%m-%d %H:%M")
    try:
        result = collection_meals.insert_one(meal_dict)
        meal_dict["_id"] = result.inserted_id
        print(f"Created meal: {meal_dict} with id: {result.inserted_id}")
        return meal_dict
    except Exception as e:
        print(f"Error creating meal: {e}")
        return {"error": str(e)}


@tool
def update_meal(id: str, meal: MealCreate) -> Optional[Dict[str, Any]]:
    """Edit an existing meal in the database.

    Args:
        id (str): MongoDB _id of meal to edit
        meal (MealCreate): Updated meal object

    Returns:
        Optional[Dict[str, Any]]: Updated meal object with _id
    """
    db = get_mongo_db()
    collection_meals = db[os.getenv("MONGO_COLLECTION_MEALS")]
    result = collection_meals.update_one(
        {"_id": id}, {"$set": meal.to_dict()})
    if result.modified_count > 0:
        return get_meal_by_id(id)
    return None


@tool
def delete_meal(id: str) -> str:
    """Delete a meal from the database.

    Args:
        id (str): MongoDB _id of meal to delete
    """
    db = get_mongo_db()
    collection_meals = db[os.getenv("MONGO_COLLECTION_MEALS")]
    result = collection_meals.delete_one({'_id': ObjectId(id)})
    return result.deleted_count > 0


@tool
def get_total_kcal(date: str = datetime.now()) -> int:
    """Get the total kcal for a specific day.
    """
    meals = get_meals_by_day(date)
    total_kcal = sum(meal.calories for meal in meals)
    return total_kcal


if __name__ == "__main__":

    raw_data = {
        'date': '2025-04-03 19:13',
        'name': "McDonald's Cheeseburger Meal, small",
        'description': 'A small meal consisting of a cheeseburger, small fries, and a small Coca-Cola.',
        'calories': 670,
        'category': 'Dinner'
    }
    meal_object = MealCreate(**raw_data)
    print(meal_object)
    print(type(meal_object))
    print("========== Create Meal ==========")
    create_meal(meal_object)
    meals = get_meals_by_day(datetime.now())
    created_meal = list(filter(lambda x: x.name == "Test Meal1", meals))
    created_meal_id = created_meal[0]._id
    print(tabulate([meal.to_dict()
          for meal in meals], headers="keys", tablefmt="grid"))

    # print("========== Edit Meal ==========")
    # update_meal(
    #     created_meal_id,
    #     MealCreate(
    #         name="Updated Meal1",
    #         calories=200,
    #         category="Lunch",
    #         date=datetime.now(),
    #         description="Updated Description1",
    #     ),
    # )
    # meals = get_meals_by_day(datetime.now())
    # print(tabulate([meal.to_dict()
    #       for meal in meals], headers="keys", tablefmt="grid"))

    # print("========== Delete Meal ==========")
    # delete_meal(created_meal_id)
    # meals = get_meals_by_day(datetime.now())
    # print(tabulate([meal.to_dict()
    #       for meal in meals], headers="keys", tablefmt="grid"))
