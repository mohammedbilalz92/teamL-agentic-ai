"""
Flask API Server for RAG Chat
Provides REST API endpoints for the Angular chat UI.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add current directory to path to import chat
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chat import RAGChat

app = Flask(__name__)
CORS(app)  # Enable CORS for Angular frontend

# Initialize RAG Chat
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "amstat_transcripts"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') 
CHAT_MODEL = "gpt-4.1-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# Initialize chat instance
rag_chat = RAGChat(
    qdrant_url=QDRANT_URL,
    collection_name=COLLECTION_NAME,
    openai_api_key=OPENAI_API_KEY,
    chat_model=CHAT_MODEL,
    embedding_model=EMBEDDING_MODEL,
    top_k=5
)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'API is running'})


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint that processes user messages.
    
    Request body:
    {
        "message": "user question",
        "show_sources": true
    }
    
    Response:
    {
        "response": "AI response text",
        "sources": [...],
        "status": "success"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing message field',
                'status': 'error'
            }), 400
        
        user_message = data['message']
        show_sources = data.get('show_sources', True)
        
        # Get response from RAG chat
        result = rag_chat.chat(user_message, show_sources=show_sources)
        
        return jsonify({
            'response': result['response'],
            'sources': result.get('sources', []),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/search', methods=['POST'])
def search():
    """
    Search endpoint that only searches vector DB without generating response.
    
    Request body:
    {
        "query": "search query",
        "top_k": 5
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing query field',
                'status': 'error'
            }), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)
        
        # Search vector database
        results = rag_chat.search_vector_db(query, top_k=top_k)
        
        return jsonify({
            'results': results,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


if __name__ == '__main__':
    print("Starting Flask API server...")
    print(f"API will be available at: http://localhost:5000")
    print(f"CORS enabled for Angular frontend")
    app.run(host='0.0.0.0', port=5000, debug=True)

