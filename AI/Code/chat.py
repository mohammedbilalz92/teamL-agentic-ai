"""
RAG Chat Interface for Amstat Transcripts
Uses Qdrant vector database for retrieval and OpenAI for generation.
"""

import os
from typing import List, Dict, Any, Optional

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("Warning: Qdrant client not installed. Install with: pip install qdrant-client")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not installed. Install with: pip install openai")


class RAGChat:
    """RAG Chat interface for querying Amstat transcripts."""
    
    def __init__(self,
                 qdrant_url: str = "http://localhost:6333",
                 collection_name: str = "amstat_transcripts",
                 openai_api_key: Optional[str] = None,
                 chat_model: str = "gpt-4.1-mini",
                 embedding_model: str = "text-embedding-3-small",
                 top_k: int = 5):
        """
        Initialize the RAG chat interface.
        
        Args:
            qdrant_url: Qdrant server URL
            collection_name: Name of the collection
            openai_api_key: OpenAI API key
            chat_model: OpenAI model for chat (gpt-4.1-mini)
            embedding_model: OpenAI model for embeddings
            top_k: Number of relevant chunks to retrieve
        """
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self.top_k = top_k
        
        # Initialize Qdrant client
        if QDRANT_AVAILABLE:
            self.qdrant_client = QdrantClient(url=qdrant_url)
        else:
            raise ImportError("Qdrant client not available. Install with: pip install qdrant-client")
        
        # Initialize OpenAI client
        if OPENAI_AVAILABLE:
            api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                self.use_ai = True
            else:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        else:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            raise
    
    def search_vector_db(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Search the vector database for relevant chunks.
        
        Args:
            query: User query
            top_k: Number of results to return (defaults to self.top_k)
            
        Returns:
            List of relevant chunks with metadata
        """
        if top_k is None:
            top_k = self.top_k
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        # Search in Qdrant
        try:
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    'id': result.payload.get('id', ''),
                    'score': result.score,
                    'chunk_text': result.payload.get('chunk_text', ''),
                    'title': result.payload.get('title', ''),
                    'source': result.payload.get('source', ''),
                    'topic': result.payload.get('topic', ''),
                    'timestamp_start': result.payload.get('timestamp_start', ''),
                    'timestamp_end': result.payload.get('timestamp_end', '')
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching vector database: {str(e)}")
            raise
    
    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks into context for the LLM.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"""
[Source {i}]
Title: {chunk.get('title', 'N/A')}
Topic: {chunk.get('topic', 'N/A')}
Source: {chunk.get('source', 'N/A')}
Timestamp: {chunk.get('timestamp_start', '')} - {chunk.get('timestamp_end', '')}
Relevance Score: {chunk.get('score', 0):.3f}

Content:
{chunk.get('chunk_text', '')}
""")
        
        return "\n".join(context_parts)
    
    def generate_response(self, query: str, context: str) -> str:
        """
        Generate a response using OpenAI based on the query and context.
        
        Args:
            query: User query
            context: Retrieved context from vector database
            
        Returns:
            Generated response
        """
        system_prompt = """You are a helpful assistant for Amstat, an aircraft data and analytics platform. 
You answer questions based on the provided video transcripts and documentation.

Guidelines:
- Answer ONLY what is asked - be direct and focused
- Do not provide extra information beyond what was asked
- Be concise and to the point
- Use the exact terminology from the transcripts
- If the information is not in the context, say so clearly
- Do not include source citations in the main answer unless specifically asked"""

        user_prompt = f"""Based on the following context from Amstat video transcripts, answer ONLY the user's specific question. 
Do not provide additional information beyond what was asked. Be direct and concise.

CONTEXT:
{context}

USER QUESTION: {query}

Provide a focused answer that directly addresses the question. If the information is not available in the context, say so clearly."""

        try:
            response = self.openai_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more focused, consistent answers
                max_tokens=500  # Reduced max tokens to keep answers concise
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            raise
    
    def chat(self, query: str, show_sources: bool = True) -> Dict[str, Any]:
        """
        Complete RAG chat flow: search, retrieve, and generate.
        
        Args:
            query: User query
            show_sources: Whether to include source information in response
            
        Returns:
            Dictionary with response and sources
        """
        print(f"\n[Searching] Looking for relevant information...")
        
        # Search vector database
        relevant_chunks = self.search_vector_db(query)
        
        if not relevant_chunks:
            return {
                'response': "I couldn't find any relevant information in the database.",
                'sources': []
            }
        
        print(f"[Found] Retrieved {len(relevant_chunks)} relevant chunk(s)")
        
        # Format context
        context = self.format_context(relevant_chunks)
        
        # Generate response
        print(f"[Generating] Creating response...")
        response = self.generate_response(query, context)
        
        result = {
            'response': response,
            'sources': relevant_chunks if show_sources else []
        }
        
        return result
    
    def interactive_chat(self):
        """Run an interactive chat session."""
        print("="*70)
        print("Amstat Transcript RAG Chat")
        print("="*70)
        print(f"Model: {self.chat_model}")
        print(f"Collection: {self.collection_name}")
        print(f"Qdrant: {self.qdrant_url}")
        print("\nType 'quit' or 'exit' to end the chat")
        print("Type 'clear' to clear the screen")
        print("-"*70)
        
        conversation_history = []
        
        while True:
            try:
                # Get user input
                user_query = input("\n[You] ").strip()
                
                if not user_query:
                    continue
                
                # Handle commands
                if user_query.lower() in ['quit', 'exit', 'q']:
                    print("\n[Goodbye] Thanks for using Amstat RAG Chat!")
                    break
                
                if user_query.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                
                # Get response
                result = self.chat(user_query, show_sources=True)
                
                # Display response
                print(f"\n[Assistant] {result['response']}")
                
                # Display sources (optional - can be toggled)
                show_sources = True  # Set to False to hide sources
                if show_sources and result['sources']:
                    print(f"\n[Sources] ({len(result['sources'])}):")
                    for i, source in enumerate(result['sources'], 1):
                        print(f"  {i}. [{source.get('topic', 'N/A')}] - {source.get('title', 'N/A')}")
                        print(f"     Score: {source.get('score', 0):.3f} | Timestamp: {source.get('timestamp_start', '')} - {source.get('timestamp_end', '')}")
                
                # Store in conversation history
                conversation_history.append({
                    'user': user_query,
                    'assistant': result['response']
                })
                
            except KeyboardInterrupt:
                print("\n\n[Goodbye] Thanks for using Amstat RAG Chat!")
                break
            except Exception as e:
                print(f"\n[ERROR] {str(e)}")
                continue


def main():
    """Main function to run the chat interface."""
    # Configuration
    QDRANT_URL = "http://localhost:6333"
    COLLECTION_NAME = "amstat_transcripts"
    
    # OpenAI configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    CHAT_MODEL = "gpt-4.1-mini"
    EMBEDDING_MODEL = "text-embedding-3-small"
    TOP_K = 5  # Number of relevant chunks to retrieve
    
    try:
        # Initialize chat interface
        chat = RAGChat(
            qdrant_url=QDRANT_URL,
            collection_name=COLLECTION_NAME,
            openai_api_key=OPENAI_API_KEY,
            chat_model=CHAT_MODEL,
            embedding_model=EMBEDDING_MODEL,
            top_k=TOP_K
        )
        
        # Run interactive chat
        chat.interactive_chat()
        
    except Exception as e:
        print(f"Error initializing chat: {str(e)}")
        print("\nMake sure:")
        print("1. Qdrant is running at http://localhost:6333")
        print("2. Collection 'amstat_transcripts' exists and has data")
        print("3. OpenAI API key is set correctly")
        print("4. Required packages are installed: pip install qdrant-client openai")


if __name__ == '__main__':
    main()

