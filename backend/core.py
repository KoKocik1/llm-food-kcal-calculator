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

    result = qa.invoke({"input": query, "chat_history": chat_history})

    new_result = {
        "query": result["input"],
        "result": result["answer"],
        "source_documents": result["context"],
    }
    return new_result
