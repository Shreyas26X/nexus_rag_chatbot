import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

# LangChain & Vector Store Imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

app = Flask(__name__)
CORS(app)

# Ensure upload folder exists
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('./chroma_db', exist_ok=True)

# 1. Database Connections
mongo_client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = mongo_client["rag_chatbot_db"]
history_collection = db["chat_histories"]

# 2. Initialize Gemini Embeddings & LLM
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=os.getenv("GEMINI_API_KEY"))
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))

# Global pointer for our local vector store persistence
vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint to verify backend status."""
    return jsonify({
        "status": "online",
        "service": "Nexus RAG Chatbot API",
        "version": "1.1.0"
    }), 200

@app.route('/api/stats', methods=['GET'])
def stats():
    """Return vector store statistics and total indexed chunks."""
    try:
        total_chunks = vector_store._collection.count() if vector_store and vector_store._collection else 0
        return jsonify({
            "status": "ready",
            "total_chunks_indexed": total_chunks,
            "vector_store": "ChromaDB",
            "embedding_model": "gemini-embedding-2"
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve vector store statistics: {str(e)}"}), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_chat_history():
    """Clear conversational memory for the active session."""
    data = request.json or {}
    session_id = data.get('session_id', 'default_session')
    history_collection.delete_one({"session_id": session_id})
    return jsonify({"message": f"Conversation history for session '{session_id}' cleared successfully."}), 200

@app.route('/api/upload', methods=['POST'])
def upload_file():
    global vector_store
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filename = file.filename.lower()
    if file and (filename.endswith('.pdf') or filename.endswith('.txt') or filename.endswith('.md')):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        try:
            # Load and parse document
            if filename.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
                documents = loader.load()
            else:
                from langchain_community.document_loaders import TextLoader
                loader = TextLoader(file_path, encoding='utf-8')
                documents = loader.load()

            # Split document into manageable chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(documents)

            # Store embeddings in ChromaDB
            vector_store = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
            
            # Clean up local file after processing
            os.remove(file_path)
            return jsonify({"message": f"Successfully indexed {file.filename}. Ready for queries."}), 200

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"error": f"Failed to process document: {str(e)}"}), 500
            
    return jsonify({"error": "Only PDF and TXT files are supported"}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    global vector_store
    data = request.json or {}
    user_query = data.get('message')
    session_id = data.get('session_id', 'default_session')

    if not user_query:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Perform similarity semantic search over the vector store
        docs = vector_store.similarity_search(user_query, k=4)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Fetch recent conversational history from MongoDB
        session_record = history_collection.find_one({"session_id": session_id})
        history = session_record['history'] if session_record else []
        formatted_history = "\n".join([f"User: {h['user']}\nAI: {h['bot']}" for h in history[-5:]])

        # System prompt ensuring grounding in verified context
        system_prompt = (
            "You are an advanced, context-aware AI assistant. Answer the user's question using exclusively "
            "the verified context provided below. If the answer cannot be found in the context, say "
            "'I cannot find that information in the uploaded documents.'\n\n"
            f"--- VERIFIED CONTEXT ---\n{context}\n\n"
            f"--- RECENT CONVERSATION HISTORY ---\n{formatted_history}\n\n"
            f"User Question: {user_query}"
        )

        # Generate response from Gemini
        response = llm.invoke(system_prompt)
        ai_response = response.content

        # Update MongoDB interaction log
        history_collection.update_one(
            {"session_id": session_id},
            {"$push": {"history": {"user": user_query, "bot": ai_response}}},
            upsert=True
        )

        return jsonify({"response": ai_response})

    except Exception as e:
        return jsonify({"error": f"An error occurred during inference: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)