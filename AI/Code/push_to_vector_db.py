"""
Push chunks to Qdrant Vector Database
Reads chunks from JSONL files and pushes them to Qdrant with embeddings.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
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


class VectorDBPusher:
    """Pushes chunks to Qdrant vector database."""
    
    def __init__(self, 
                 qdrant_url: str = "http://localhost:6333",
                 collection_name: str = "amstat_transcripts",
                 openai_api_key: Optional[str] = None,
                 embedding_model: str = "text-embedding-3-small"):
        """
        Initialize the vector DB pusher.
        
        Args:
            qdrant_url: Qdrant server URL
            collection_name: Name of the collection to create/use
            openai_api_key: OpenAI API key for embeddings
            embedding_model: OpenAI embedding model to use
        """
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Initialize Qdrant client
        if QDRANT_AVAILABLE:
            self.qdrant_client = QdrantClient(url=qdrant_url)
        else:
            raise ImportError("Qdrant client not available. Install with: pip install qdrant-client")
        
        # Initialize OpenAI client for embeddings
        if OPENAI_AVAILABLE:
            api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                self.use_embeddings = True
            else:
                print("Warning: OpenAI API key not found. Cannot generate embeddings.")
                self.openai_client = None
                self.use_embeddings = False
        else:
            self.openai_client = None
            self.use_embeddings = False
    
    def create_collection(self, vector_size: int = 1536):
        """
        Create or get the Qdrant collection.
        
        Args:
            vector_size: Size of embedding vectors (1536 for text-embedding-3-small, 3072 for text-embedding-3-large)
        """
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if not collection_exists:
                print(f"Creating collection '{self.collection_name}'...")
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Collection '{self.collection_name}' created successfully!")
            else:
                print(f"Collection '{self.collection_name}' already exists.")
        except Exception as e:
            print(f"Error creating collection: {str(e)}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if not self.use_embeddings or not self.openai_client:
            raise ValueError("OpenAI client not initialized. Provide API key.")
        
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            raise
    
    def load_chunks_from_jsonl(self, jsonl_file: str) -> List[Dict[str, Any]]:
        """
        Load chunks from a JSONL file.
        
        Args:
            jsonl_file: Path to JSONL file
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    chunk = json.loads(line)
                    chunks.append(chunk)
        return chunks
    
    def prepare_points(self, chunks: List[Dict[str, Any]], start_id: int = 0) -> List[PointStruct]:
        """
        Prepare Qdrant points from chunks.
        
        Args:
            chunks: List of chunk dictionaries
            start_id: Starting ID for points
            
        Returns:
            List of PointStruct objects
        """
        points = []
        
        for idx, chunk in enumerate(chunks):
            # Get embedding
            chunk_text = chunk.get('chunk_text', chunk.get('text', ''))
            if not chunk_text:
                print(f"Warning: Empty chunk text for chunk {idx}, skipping...")
                continue
            
            try:
                embedding = self.get_embedding(chunk_text)
            except Exception as e:
                print(f"Error generating embedding for chunk {idx}: {str(e)}")
                continue
            
            # Create point
            point = PointStruct(
                id=start_id + idx,
                vector=embedding,
                payload={
                    'id': chunk.get('id', f'chunk_{start_id + idx}'),
                    'title': chunk.get('title', ''),
                    'source': chunk.get('source', ''),
                    'chunk_text': chunk_text,
                    'metadata': chunk.get('metadata', {}),
                    'timestamp_start': chunk.get('metadata', {}).get('timestamp_start', ''),
                    'timestamp_end': chunk.get('metadata', {}).get('timestamp_end', ''),
                    'topic': chunk.get('metadata', {}).get('topic', ''),
                    'processed_date': datetime.now().isoformat()
                }
            )
            points.append(point)
        
        return points
    
    def push_chunks(self, chunks: List[Dict[str, Any]], start_id: int = 0, batch_size: int = 100):
        """
        Push chunks to Qdrant.
        
        Args:
            chunks: List of chunk dictionaries
            start_id: Starting ID for points
            batch_size: Number of points to upload in each batch
        """
        if not chunks:
            print("No chunks to push.")
            return
        
        print(f"Preparing {len(chunks)} chunks for upload...")
        
        # Prepare points
        points = self.prepare_points(chunks, start_id)
        
        if not points:
            print("No valid points to upload.")
            return
        
        # Upload in batches
        total_points = len(points)
        uploaded = 0
        
        for i in range(0, total_points, batch_size):
            batch = points[i:i + batch_size]
            try:
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                uploaded += len(batch)
                print(f"Uploaded {uploaded}/{total_points} points...")
            except Exception as e:
                print(f"Error uploading batch {i//batch_size + 1}: {str(e)}")
                raise
        
        print(f"Successfully uploaded {uploaded} points to collection '{self.collection_name}'!")
    
    def process_all_files(self, processed_dir: str):
        """
        Process all JSONL files in the processed directory.
        
        Args:
            processed_dir: Directory containing processed files
        """
        processed_path = Path(processed_dir)
        
        # Find all chunks.jsonl files
        jsonl_files = list(processed_path.rglob('chunks.jsonl'))
        
        if not jsonl_files:
            print(f"No chunks.jsonl files found in {processed_dir}")
            return
        
        print(f"Found {len(jsonl_files)} JSONL file(s) to process\n")
        
        # Create collection (determine vector size from first embedding)
        if self.use_embeddings:
            # Test embedding to get vector size
            test_embedding = self.get_embedding("test")
            vector_size = len(test_embedding)
            print(f"Detected embedding vector size: {vector_size}")
            self.create_collection(vector_size)
        else:
            raise ValueError("Cannot create collection without embeddings. Provide OpenAI API key.")
        
        # Process each file
        total_chunks = 0
        current_id = 0
        
        for jsonl_file in jsonl_files:
            try:
                print(f"\nProcessing: {jsonl_file}")
                chunks = self.load_chunks_from_jsonl(str(jsonl_file))
                print(f"  -> Loaded {len(chunks)} chunks")
                
                if chunks:
                    self.push_chunks(chunks, start_id=current_id)
                    current_id += len(chunks)
                    total_chunks += len(chunks)
                    
            except Exception as e:
                print(f"Error processing {jsonl_file}: {str(e)}")
                continue
        
        print(f"\n{'='*60}")
        print(f"Processing complete!")
        print(f"Total chunks uploaded: {total_chunks}")
        print(f"Collection: {self.collection_name}")
        print(f"Qdrant URL: {self.qdrant_url}")
        
        # Get collection info
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            print(f"\nCollection info:")
            print(f"  - Points count: {collection_info.points_count}")
            print(f"  - Vector size: {collection_info.config.params.vectors.size}")
            print(f"  - Distance metric: {collection_info.config.params.vectors.distance}")
        except Exception as e:
            print(f"Could not retrieve collection info: {str(e)}")


def main():
    """Main function to push chunks to vector DB."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Configuration
    PROCESSED_DIR = os.path.join(project_root, 'Processed_Files')
    QDRANT_URL = "http://localhost:6333"
    COLLECTION_NAME = "amstat_transcripts"
    
    # OpenAI configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') 
    EMBEDDING_MODEL = "text-embedding-3-small"  # or "text-embedding-3-large" for better quality
    
    print("="*60)
    print("Pushing chunks to Qdrant Vector Database")
    print("="*60)
    print(f"Qdrant URL: {QDRANT_URL}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Processed Files Directory: {PROCESSED_DIR}")
    print()
    
    # Initialize pusher
    try:
        pusher = VectorDBPusher(
            qdrant_url=QDRANT_URL,
            collection_name=COLLECTION_NAME,
            openai_api_key=OPENAI_API_KEY,
            embedding_model=EMBEDDING_MODEL
        )
        
        # Process all files
        pusher.process_all_files(PROCESSED_DIR)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nMake sure:")
        print("1. Qdrant is running at http://localhost:6333")
        print("2. OpenAI API key is set correctly")
        print("3. Required packages are installed: pip install qdrant-client openai")


if __name__ == '__main__':
    main()

