# rag_chain.py
import os
import warnings
from langchain_community.vectorstores import FAISS

# Suppress LangChain deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "tn_agriculture_faiss_db"

def get_rag_chain():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Check if vector DB exists
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Vector database not found at {DB_PATH}. Please run vector_store.py first.")
        
    vectorstore = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    # --- RTCFR STRUCTURED SYSTEM PROMPT ---
    SYSTEM_PROMPT = (
        "**[Role]** You are an expert Agricultural Extension Officer and AI assistant dedicated to Tamil Nadu farmers, "
        "specializing in official government schemes, subsidies, micro-irrigation, mechanization, and welfare services.\n\n"
        
        "**[Task]** Answer the farmer's query accurately regarding eligibility, subsidy percentages, application steps, "
        "and required documents. Support bilingual communication in English, Tamil (தமிழ்), and Tanglish based on user input.\n\n"
        
        "**[Context]** Use *strictly* and *only* the official government portal data provided in the retrieved context below. "
        "Do not invent external schemes or assumptions.\n\n"
        
        "**[Format]** Structure your response clearly with:\n"
        "1. **Scheme Summary / திட்டம் சுருக்கம்**\n"
        "2. **Subsidy & Benefits / மானியம் மற்றும் பலன்கள்**\n"
        "3. **Eligibility / தகுதி வரம்பு**\n"
        "4. **How to Apply / விண்ணப்பிக்கும் முறை**\n\n"
        
        "**[Rules]** If the exact answer is not present in the context, politely state that the information is currently "
        "unavailable in the official portal database and advise checking the local agricultural extension center.\n\n"
        
        "Retrieved Context:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    return rag_chain

def query_rag_with_sources(user_input: str, chat_history: list = None):
    if chat_history is None:
        chat_history = []
    try:
        chain = get_rag_chain()
        response = chain.invoke({"input": user_input, "chat_history": chat_history})
        
        answer = response.get("answer", "No response generated.")
        sources = set([doc.metadata.get("source", "Official TN Portal") for doc in response.get("context", [])])
        
        return {
            "answer": answer,
            "sources": list(sources)
        }
    except Exception as e:
        return {
            "answer": f"Error querying agricultural database: {e}",
            "sources": []
        }