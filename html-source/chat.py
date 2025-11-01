from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
import os

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Vector Embeddings - using the same model as during indexing
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

# Connect to existing vector database collection
vector_db = QdrantVectorStore.from_existing_collection(
    url=os.getenv("QDRANT_URL"),
    collection_name="html-rag",
    embedding=embedding_model
)

print("💬 HTML Content Chat (Enhanced)")
print("=" * 50)
print("Type 'quit', 'exit', or 'q' to end the conversation\n")

# Continuous chat loop
while True:
    # Take user input
    user_query = input("❓ You: ").strip()
    
    if user_query.lower() in ['quit', 'exit', 'q', '']:
        print("\n👋 Goodbye!")
        break
    
    # Search for relevant chunks from the vector database
    search_results = vector_db.similarity_search(query=user_query, k=5)
    
    # Format the context from search results
    context_parts = []
    sources_seen = set()
    
    for idx, result in enumerate(search_results, 1):
        filename = result.metadata.get('filename', 'Unknown')
        source_path = result.metadata.get('source', 'Unknown')
        sources_seen.add(filename if filename != 'Unknown' else source_path)
        
        context_parts.append(
            f"--- Chunk {idx} ---\n"
            f"Content: {result.page_content}\n"
            f"Source File: {filename}\n"
            f"Path: {source_path}"
        )
    
    context = "\n\n".join(context_parts)
    
    SYSTEM_PROMPT = f"""
You are a helpful AI Assistant who answers user queries based on the available context retrieved from HTML files.

You should only answer the user based on the following context extracted from the HTML documents.
If the information is not in the context, politely say that you don't have that information.

When answering, be specific and cite which source file the information comes from if relevant.

Context:
{context}
"""
    
    # Generate response using OpenAI
    response = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ],
        temperature=0.7
    )
    
    answer = response.choices[0].message.content
    
    print(f"\n🤖 Assistant: {answer}")
    
    # Show sources
    if sources_seen:
        print(f"\n📚 Sources: {', '.join(sources_seen)}")
    
    print("\n" + "-" * 50 + "\n")


