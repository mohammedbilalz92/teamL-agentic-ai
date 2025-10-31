from pathlib import Path
from langchain_community.document_loaders import BSHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()

docs_dir = Path(__file__).parent / "docs"

# Load all HTML files from the docs directory
all_docs = []
html_files = list(docs_dir.glob("*.html"))

print(f"Found {len(html_files)} HTML file(s) in {docs_dir}")

for html_file in html_files:
    print(f"\nProcessing: {html_file.name}")
    
    # Load HTML file using BeautifulSoup-based loader
    loader = BSHTMLLoader(
        file_path=str(html_file),
        open_encoding="utf-8",
        bs_kwargs={"features": "html.parser"}
    )
    
    docs = loader.load()
    
    # Add filename to metadata for better tracking
    for doc in docs:
        doc.metadata["filename"] = html_file.name
    
    all_docs.extend(docs)
    print(f"  ✓ Loaded {len(docs)} document(s) from {html_file.name}")

print(f"\n📊 Total documents loaded: {len(all_docs)}")

if len(all_docs) == 0:
    print("❌ No HTML files found to process!")
    exit(1)

# Split the docs into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)

chunks = text_splitter.split_documents(documents=all_docs)
print(f"📝 Created {len(chunks)} chunks from all HTML documents")

# Vector embeddings using OpenAI's text embedding model
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

print("🔄 Creating embeddings and storing in Qdrant...")

# Store chunks in Qdrant vector database
vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="html-rag"
)

print("\n✅ All HTML content successfully indexed in Qdrant vector store!")
print(f"📦 Collection name: html-rag")
print(f"📚 Total chunks stored: {len(chunks)}")
print(f"📄 Files processed: {len(html_files)}")


