from dotenv import load_dotenv
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_experimental.tools import PythonREPLTool
from typing import Dict, Any

load_dotenv()


def create_calories_agent() -> AgentExecutor:
    """Create an agent that calculates calories from meal descriptions."""
    instructions = """
    You are an agent designed to calculate calories from meal descriptions.
    You have access to a python REPL, which you can use to execute python code.
    You need to calculate the calories for a meal based on the ingredients and portions.
    You should:
    1. Break down the meal into its components
    2. Estimate portions in standard units (grams, pieces, etc.)
    3. Calculate calories for each component
    4. Sum all components to get the total calories
    5. Return the total calories as a single number
    
    If you get an error, debug your code and try again.
    Only use the output of your code to answer the question.
    If it does not seem like you can write code to answer the question, just return "-1" as the answer.
    """

    base_prompt = hub.pull("langchain-ai/react-agent-template")
    prompt = base_prompt.partial(instructions=instructions)

    tools = [PythonREPLTool()]
    calories_agent = create_react_agent(
        prompt=prompt,
        llm=ChatOpenAI(temperature=0, model="gpt-4-turbo"),
        tools=tools,
    )

    return AgentExecutor(agent=calories_agent, tools=tools, verbose=True)


def calculate_meal_calories(meal_description: str) -> Dict[str, Any]:
    """Calculate calories for a meal description."""
    agent = create_calories_agent()
    result = agent.invoke({
        "input": f"Calculate the total calories for this meal: {meal_description}"
    })

    try:
        calories = int(result["output"])
        return {
            "calories": calories,
            "success": True
        }
    except ValueError:
        return {
            "calories": -1,
            "success": False,
            "error": "Could not calculate calories"
        }
