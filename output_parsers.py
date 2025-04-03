from typing import Dict, Any
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class MealInfo(BaseModel):
    name: str = Field(description="name of the meal")
    description: str = Field(description="short description of the meal")
    calories: int = Field(description="calories in the meal")
    category: str = Field(description="category of the meal")
    date: str = Field(description="date of the meal")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "calories": self.calories,
            "category": self.category,
            "date": self.date
        }


meal_info_parser = PydanticOutputParser(pydantic_object=MealInfo)
