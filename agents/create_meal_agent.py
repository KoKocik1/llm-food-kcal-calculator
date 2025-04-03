from datetime import datetime
from typing import Dict, Any
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_experimental.tools import PythonREPLTool
from db.category_service import get_categories
from agents.calories_agent import calculate_meal_calories
from model.mealCreate import MealCreate
from db.meal_service import create_meal as db_create_meal


def create_meal_agent() -> AgentExecutor:
    """Create an agent that handles meal creation with proper categorization."""
    instructions = """
    You are an agent designed to create meal entries with proper categorization and calorie calculation.
    You have access to a python REPL, which you can use to execute python code.
    
    For each meal description, you should:
    1. Determine the appropriate category from the available categories
    2. Generate a concise name for the meal
    3. Create a detailed description of the ingredients
    4. Calculate the total calories
    5. Format the date and time
    
    Available categories: {categories}
    
    Return the meal information in a structured format.
    If you get an error, debug your code and try again.
    Only use the output of your code to answer the question.
    """

    base_prompt = hub.pull("langchain-ai/react-agent-template")
    prompt = base_prompt.partial(
        instructions=instructions,
        categories=get_categories()
    )

    tools = [PythonREPLTool()]
    meal_agent = create_react_agent(
        prompt=prompt,
        llm=ChatOpenAI(temperature=0, model="gpt-4-turbo"),
        tools=tools,
    )

    return AgentExecutor(agent=meal_agent, tools=tools, verbose=True)


def create_meal_from_description(description: str) -> Dict[str, Any]:
    """Create a meal entry from a description."""
    # First, calculate calories
    calories_result = calculate_meal_calories(description)
    if not calories_result["success"]:
        return {
            "success": False,
            "error": "Failed to calculate calories"
        }

    # Then, create the meal with proper categorization
    agent = create_meal_agent()
    result = agent.invoke({
        "input": f"Create a meal entry for: {description}"
    })

    try:
        # Parse the agent's output and create the meal
        meal_data = {
            "name": result["output"].get("name", "Unnamed Meal"),
            "description": description,
            "calories": calories_result["calories"],
            "category": result["output"].get("category", "Other"),
            "date": datetime.now()
        }

        meal = MealCreate(**meal_data)
        saved_meal = db_create_meal(meal)

        return {
            "success": True,
            "meal": saved_meal
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
