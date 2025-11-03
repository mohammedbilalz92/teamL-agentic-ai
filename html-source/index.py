from pathlib import Path
from langchain_community.document_loaders import BSHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()

html_path = Path(__file__).parent / "docs/amstat-premier-aircraft-spec-page.html"

# Load HTML file using BeautifulSoup-based loader
# This loader extracts text content while filtering out scripts and styles
loader = BSHTMLLoader(
    file_path=str(html_path),
    open_encoding="utf-8",
    bs_kwargs={"features": "html.parser"}
)
docs = loader.load()

#print(f"Loaded {len(docs)} HTML document(s)")
#print(f"First document preview (first 500 chars): {docs[0].page_content[:500]}")

# Split the docs into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)

chunks = text_splitter.split_documents(documents=docs)
print(f"Created {len(chunks)} chunks from the HTML document")

# Vector embeddings using OpenAI's text embedding model
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

# Store chunks in Qdrant vector database
vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="html-rag"
)

print("✅ HTML content successfully indexed in Qdrant vector store!")
print(f"Collection name: html-rag")
print(f"Total chunks stored: {len(chunks)}")
