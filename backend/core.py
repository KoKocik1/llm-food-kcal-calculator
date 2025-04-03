from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from model.mealCreate import MealCreate
from db.category_service import get_categories
from db.meal_service import create_meal as db_create_meal, update_meal as db_update_meal, get_meals_by_date_range
from output_parsers import meal_info_parser
from tabulate import tabulate
load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
LANGCHAIN_HUB = "langchain-ai/retrieval-qa-chat"
LANGCHAIN_REPHRASE_HUB = "langchain-ai/chat-langchain-rephrase"


def run_llm(query, chat_history: List[Dict[str, Any]]):
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = PineconeVectorStore(
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        embedding=embeddings,
    )
    chat = ChatOpenAI(model="gpt-4o-mini", temperature=0, verbose=True)

    # History Aware Retrieval
    rephrase_prompt = hub.pull(LANGCHAIN_REPHRASE_HUB)
    history_aware_retriever = create_history_aware_retriever(
        llm=chat, retriever=vectorstore.as_retriever(), prompt=rephrase_prompt
    )

    # Retrieval QA Chat
    retrieval_qa_chat_prompt = hub.pull(LANGCHAIN_HUB)
    stuff_documents_chain = create_stuff_documents_chain(
        chat, retrieval_qa_chat_prompt)

    qa = create_retrieval_chain(
        retriever=history_aware_retriever,
        combine_docs_chain=stuff_documents_chain,
    )

    # Add specific formatting instructions to the query
    formatted_query = f"""
    Please provide information about {query} in the following json format:
    - name: Name of the food/meal
    - description: Detailed description
    - calories: Calories (as a number)
    - category: One of: {get_categories()}
    - date: Date of the meal in YYYY-MM-DD HH:MM format, Today is: {datetime.now().strftime("%Y-%m-%d %H:%M")}
    If you can't find the information, you return a question to the user to specify.
    """

    result = qa.invoke(
        {"input": formatted_query, "chat_history": chat_history})

    # Parse the response to ensure it has the required fields
    answer = result["answer"]
    new_result = {
        "query": result["input"],
        "result": answer,
        "source_documents": result["context"],
    }
    return new_result


def get_meal_chain() -> Any:
    """Create a chain for meal-related operations."""
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = PineconeVectorStore(
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        embedding=embeddings,
    )
    chat = ChatOpenAI(model="gpt-4o-mini", temperature=0, verbose=True)

    # History Aware Retrieval
    rephrase_prompt = hub.pull(LANGCHAIN_REPHRASE_HUB)
    history_aware_retriever = create_history_aware_retriever(
        llm=chat, retriever=vectorstore.as_retriever(), prompt=rephrase_prompt
    )

    # Retrieval QA Chat
    retrieval_qa_chat_prompt = hub.pull(LANGCHAIN_HUB)
    stuff_documents_chain = create_stuff_documents_chain(
        chat, retrieval_qa_chat_prompt)

    return create_retrieval_chain(
        retriever=history_aware_retriever,
        combine_docs_chain=stuff_documents_chain,
    )


def create_meal(query: str, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a new meal entry based on user query."""
    qa = get_meal_chain()

    # First, get meal information from Pinecone
    meal_info_query = f"""
    Tell me about the nutritional information and calories for: {query}.
    Format your response as valid JSON with the following fields: name, description, calories, category, date.
    The date should be today's date in YYYY-MM-DD HH:MM format. If the time is not specified, use the current time.
    The category should be one of the following: {get_categories()}
    The name should be a short description of the meal.
    The description should be a detailed description of the meal. Only describe the ingredients from the query. Don't add any other ingredients.
    The calories should be the number of calories in the meal (all the ingredients).
    """

    meal_info = qa.invoke(
        {"input": meal_info_query, "chat_history": chat_history})

    try:
        # Parse the meal information
        parsed_meal = meal_info_parser.parse(meal_info["answer"])
        meal_dict = parsed_meal.to_dict()

        # Create meal object
        meal = MealCreate(
            date=datetime.strptime(meal_dict["date"], "%Y-%m-%d %H:%M"),
            name=meal_dict["name"],
            description=meal_dict["description"],
            calories=meal_dict["calories"],
            category=meal_dict["category"]
        )

        # Save to database
        saved_meal = db_create_meal(meal)

        return {
            "query": query,
            "result": f"Created meal: {meal.name} with {meal.calories} calories",
            "meal": saved_meal
        }
    except Exception as e:
        return {
            "query": query,
            "result": "Failed to create meal",
            "error": str(e)
        }


def update_meal(meal_id: str, query: str, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Update an existing meal entry."""
    qa = get_meal_chain()

    # Get updated meal information
    meal_info_query = f"Tell me about the nutritional information and calories for: {query}. Format your response as valid JSON with the following fields: name, description, calories, category, date. The date should be today's date in YYYY-MM-DD format."
    meal_info = qa.invoke(
        {"input": meal_info_query, "chat_history": chat_history})

    try:
        # Parse the meal information
        parsed_meal = meal_info_parser.parse(meal_info["answer"])
        meal_dict = parsed_meal.to_dict()

        # Update in database
        updated_meal = db_update_meal(meal_id, meal_dict)

        if not updated_meal:
            return {
                "query": query,
                "result": "Meal not found",
                "error": "Meal with specified ID does not exist"
            }

        return {
            "query": query,
            "result": f"Updated meal: {query} with {meal_dict['calories']} calories",
            "meal": updated_meal
        }
    except Exception as e:
        return {
            "query": query,
            "result": "Failed to update meal",
            "error": str(e)
        }


if __name__ == "__main__":
    result = create_meal("I ate a hamburger", [])
    print(result)
    result = update_meal(result["meal"]["_id"],
                         "I ate a hamburger with fries", [])
