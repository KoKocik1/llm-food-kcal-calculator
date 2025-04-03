from typing import Dict, Any, List
from datetime import datetime
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import Tool
from langchain_core.tools import StructuredTool
from pydantic import BaseModel
from db.meal_service import (
    create_meal,
    update_meal,
    get_meal_by_id,
    get_meals_by_day,
    delete_meal,
    get_total_kcal
)
from agents.create_meal_agent import create_meal_from_description
from agents.calories_agent import calculate_meal_calories


class GetMealsByDayInput(BaseModel):
    date: str


def create_grand_agent() -> AgentExecutor:
    """Create the main agent that coordinates all other agents."""
    tools = [
        Tool(
            name="Create Meal",
            func=create_meal_from_description,
            description="""
            Create a new meal entry from a description.
            Input should be a natural language description of what was eaten.
            Returns a dictionary with success status and meal data.
            """
        ),
        Tool(
            name="Update Meal",
            func=update_meal,
            description="""
            Update an existing meal entry.
            Requires meal ID and updated meal data.
            Returns the updated meal or None if not found.
            """
        ),
        Tool(
            name="Get Meal by ID",
            func=get_meal_by_id,
            description="""
            Retrieve a meal by its ID.
            Returns the meal data or None if not found.
            """
        ),
        StructuredTool(
            name="Get Meals by Day",
            func=get_meals_by_day,
            description="""
            Get all meals for a specific date.
            Input should be a date in YYYY-MM-DD format.
            Returns a list of meals for that day.
            """,
            args_schema=GetMealsByDayInput,
        ),
        Tool(
            name="Delete Meal",
            func=delete_meal,
            description="""
            Delete a meal by its ID.
            Returns True if deleted, False if not found.
            """
        ),
        Tool(
            name="Get Total Calories",
            func=get_total_kcal,
            description="""
            Get total calories for a specific day.
            Input should be a date in YYYY-MM-DD format.
            Returns the total calories for that day.
            """
        ),
        Tool(
            name="Calculate Calories",
            func=calculate_meal_calories,
            description="""
            Calculate calories for a meal description.
            Input should be a natural language description of the meal.
            Returns a dictionary with calories and success status.
            """
        )
    ]

    base_prompt = hub.pull("langchain-ai/react-agent-template")
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = base_prompt.partial(
        instructions="""
        You are the main agent coordinating meal tracking operations.
        Today is {today}
        
        You can:
        1. Create new meals from descriptions
        2. Update existing meals
        3. Delete meals
        4. Get meals for specific days
        5. Calculate calories for meals
        6. Get total calories for a day
        
        Use the appropriate tools based on the user's request.
        Always provide clear, concise responses.
        If an operation fails, explain why and suggest alternatives.
        """.format(today=today)
    )

    grand_agent = create_react_agent(
        prompt=prompt,
        llm=ChatOpenAI(temperature=0, model="gpt-4-turbo"),
        tools=tools,
    )

    return AgentExecutor(agent=grand_agent, tools=tools, verbose=True)


def process_user_input(user_input: str) -> Dict[str, Any]:
    """Process user input using the grand agent."""
    agent = create_grand_agent()
    result = agent.invoke({"input": user_input})
    return result
