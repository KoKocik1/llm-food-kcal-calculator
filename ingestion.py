from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from bs4 import BeautifulSoup
from langchain_core.documents import Document
import os

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def load_html_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(separator=" ", strip=True)


def ingest_docs():
    documents = []

    for root, dirs, files in os.walk("calories_info_processed"):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                content = load_html_content(file_path)
                if content.strip():
                    documents.append(
                        Document(page_content=content, metadata={"source": file_path})
                    )

    print(f"Found {len(documents)} documents")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    for chunk in chunks:
        new_url = chunk.metadata["source"]
        new_url = new_url.replace(
            "calories_info_processed", "https://www.calorieking.com/us/en/foods"
        )
        chunk.metadata.update({"source": new_url})

    PineconeVectorStore.from_documents(
        chunks,
        embeddings,
        index_name=os.getenv("PINECONE_INDEX_NAME"),
    )
    print("Documents ingested successfully")


if __name__ == "__main__":
    ingest_docs()
