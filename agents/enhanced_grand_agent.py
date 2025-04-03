from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain import hub
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
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
from backend.core import run_llm
from output_parsers import meal_info_parser
import os
from dotenv import load_dotenv
from db.meal_service import MealCreate
load_dotenv()


class GetMealsByDayInput(BaseModel):
    date: str


def search_meal_info(query: str, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Search for meal information in the vector database."""
    result = run_llm(query, chat_history)
    return result


def create_meal_with_search(query: str, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a meal by first searching for nutritional information."""
    # First search for meal information
    search_result = search_meal_info(query, chat_history)

    try:
        # Parse the meal information
        meal_object = meal_info_parser.parse(search_result["result"])
        print("===============================")
        print(meal_object)
        meal_dict = meal_object.to_dict()
        print(meal_dict)
        meal_create = MealCreate(**meal_object)
        print(meal_create)
        print("===============================")
        # Create meal in database using the validated object
        saved_meal = create_meal(meal_create)

        # return {
        #     "query": query,
        #     "result": f"Created meal: {meal_object.name} with {meal_object.calories} calories",
        #     "meal": saved_meal,
        #     "search_info": search_result
        # source_documents
        # }
        return {
            "query": query,
            "result": f"Created meal: {meal_object.name} with {meal_object.calories} calories",
            "meal": saved_meal,
            "search_info": search_result,
        }
    except Exception as e:
        return {
            "query": query,
            "result": "Failed to create meal",
            "error": str(e),
            "search_info": search_result
        }


def create_enhanced_grand_agent() -> AgentExecutor:
    """Create the enhanced main agent that coordinates all operations including vector search."""

    def search_meal_info_wrapper(query: str) -> Dict[str, Any]:
        """Wrapper for search_meal_info that gets chat_history from the agent's context."""
        return search_meal_info(query, [])

    def create_meal_with_search_wrapper(query: str) -> Dict[str, Any]:
        """Wrapper for create_meal_with_search that gets chat_history from the agent's context."""
        return create_meal_with_search(query, [])

    tools = [
        Tool(
            name="Search Meal Information",
            func=search_meal_info_wrapper,
            description="""
            Search for nutritional information about a meal in the vector database.
            Input should be a natural language description of the meal.
            Returns detailed nutritional information and sources.
            """
        ),
        Tool(
            name="Create Meal with Search",
            func=create_meal_with_search_wrapper,
            description="""
            Create a new meal entry by first searching for nutritional information.
            Input should be a natural language description of what was eaten.
            Returns a dictionary with success status, meal data, and search information.
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
        )
    ]

    base_prompt = hub.pull("langchain-ai/react-agent-template")
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = base_prompt.partial(
        instructions="""
        You are an enhanced meal tracking assistant that can search for nutritional information and manage meals.
        Today is {today}
        
        Your capabilities:
        1. Search for nutritional information about meals using the vector database
        2. Create new meals by first searching for nutritional information
        3. Update existing meals
        4. Delete meals
        5. Get meals for specific days
        6. Get total calories for a day
        
        When creating a meal:
        1. First use the Search Meal Information tool to get nutritional details
        2. Then use Create Meal with Search to save the meal
        3. If the search results are unclear, ask the user for clarification
        
        Always provide clear, concise responses.
        If an operation fails, explain why and suggest alternatives.
        When searching for nutritional information, include relevant details from the search results in your response.
        """.format(today=today)
    )

    enhanced_agent = create_react_agent(
        prompt=prompt,
        llm=ChatOpenAI(temperature=0, model="gpt-4-turbo"),
        tools=tools,
    )

    return AgentExecutor(agent=enhanced_agent, tools=tools, verbose=True)


def process_user_input(query: str, chat_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Process user input using the enhanced grand agent."""
    if chat_history is None:
        chat_history = []

    agent = create_enhanced_grand_agent()
    result = agent.invoke({
        "input": query,
        "chat_history": chat_history
    })

    # Format the response to match the expected structure
    formatted_result = {
        "query": query,
        "result": result.get("output", result.get("result", "")),
        "source_documents": result.get("source_documents", [])
    }

    return formatted_result
