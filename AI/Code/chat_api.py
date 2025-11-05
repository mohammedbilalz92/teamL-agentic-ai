"""
FastAPI Backend for Chat Interface
Exposes the RAG chat functionality as a REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import sys

# Add parent directory to path to import chat module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat import RAGChat

app = FastAPI(title="Amstat RAG Chat API")

# Enable CORS for Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000"],  # Angular default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chat instance
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') 
try:
    chat_instance = RAGChat(
        qdrant_url="http://localhost:6333",
        collection_name="amstat_transcripts",
        openai_api_key=OPENAI_API_KEY,
        chat_model="gpt-4.1-mini",
        embedding_model="text-embedding-3-small",
        top_k=5
    )
except Exception as e:
    print(f"Warning: Could not initialize chat instance: {e}")
    chat_instance = None


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []


class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    success: bool
    error: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "Amstat RAG Chat API", "status": "running"}


@app.get("/health")
def health_check():
    if chat_instance is None:
        return {"status": "error", "message": "Chat instance not initialized"}
    return {"status": "ok", "message": "API is healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint that processes user messages and returns AI responses.
    """
    if chat_instance is None:
        raise HTTPException(status_code=500, detail="Chat service not available")
    
    try:
        # Get response from chat
        result = chat_instance.chat(request.message, show_sources=True)
        
        return ChatResponse(
            response=result['response'],
            sources=result['sources'],
            success=True
        )
    except Exception as e:
        return ChatResponse(
            response="",
            sources=[],
            success=False,
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

