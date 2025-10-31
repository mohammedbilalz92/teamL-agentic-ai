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
    url="http://localhost:6333",
    collection_name="html-rag",
    embedding=embedding_model
)

# Take user input
user_query = input("Ask something about the HTML content: ")

# Search for relevant chunks from the vector database
search_results = vector_db.similarity_search(query=user_query, k=4)

# Format the context from search results
context_parts = []
for idx, result in enumerate(search_results, 1):
    context_parts.append(
        f"--- Chunk {idx} ---\n"
        f"Content: {result.page_content}\n"
        f"Source: {result.metadata.get('source', 'Unknown')}"
    )

context = "\n\n".join(context_parts)

SYSTEM_PROMPT = f"""
You are a helpful AI Assistant who answers user queries based on the available context retrieved from an HTML file.

You should only answer the user based on the following context extracted from the HTML document.
If the information is not in the context, politely say that you don't have that information.

Context:
{context}
"""

# Generate response using OpenAI
response = openai_client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]
)

print(f"\n🤖: {response.choices[0].message.content}")


