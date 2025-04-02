from datetime import datetime


class MealCreate:
    def __init__(
        self, date: datetime, name: str, description: str, calories: int, category: str
    ):
        self.date = date
        self.name = name
        self.description = description
        self.calories = calories
        self.category = category

    def to_dict(self):
        return {
            "date": self.date,
            "name": self.name,
            "description": self.description,
            "calories": self.calories,
            "category": self.category,
        }

    def from_dict(self, meal_dict: dict):
        self.date = meal_dict["date"]
        self.name = meal_dict["name"]
        self.description = meal_dict["description"]
        self.calories = meal_dict["calories"]
        self.category = meal_dict["category"]

    def __repr__(self):
        return f"{self.to_dict()}"
