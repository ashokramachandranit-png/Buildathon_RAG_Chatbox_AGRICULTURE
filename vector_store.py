import os
import warnings
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from scraper import get_processed_chunks

# Load environment variables from .env file
load_dotenv()

warnings.filterwarnings("ignore")

INDEX_PATH = "tn_agriculture_faiss_db"


def create_or_update_vector_store():
    """Generates embeddings for processed chunks and builds/saves local FAISS vector store."""
    print("Step 1/3: Ingesting web and PDF scheme data...")
    chunks = get_processed_chunks()

    if not chunks:
        print("Error: No documents found to index.")
        return None

    print(f"Step 2/3: Generating OpenAI Embeddings for {len(chunks)} chunks...")
    
    # Retrieves OPENAI_API_KEY automatically from environment/dotenv
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    print("Step 3/3: Building FAISS Vector Index...")
    vector_db = FAISS.from_documents(chunks, embeddings)

    # Save vector DB locally
    vector_db.save_local(INDEX_PATH)
    print(f"✅ Vector database successfully built and saved to './{INDEX_PATH}'!")
    return vector_db


def load_vector_store():
    """Loads existing FAISS vector store from local disk."""
    if os.path.exists(INDEX_PATH):
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        return FAISS.load_local(
            INDEX_PATH, embeddings, allow_dangerous_deserialization=True
        )
    else:
        print(
            f"Index folder '{INDEX_PATH}' not found. Building a new vector index..."
        )
        return create_or_update_vector_store()


if __name__ == "__main__":
    create_or_update_vector_store()