# Quick Setup Guide for HTML-based RAG System

## 🚀 Quick Start

### 1. Environment Setup

**Option A: Use existing virtual environment from agentic-ai**
```powershell
# From udemy directory
.\agentic-ai\udemy-agentic-ai-venv\Scripts\Activate.ps1
```

**Option B: Create new virtual environment**
```powershell
# In html-source directory
python -m venv html-venv
.\html-venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
cd html-source
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the html-source directory:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 4. Start Qdrant Vector Database

From the parent directory (udemy/):
```powershell
docker-compose up -d
```

Verify Qdrant is running:
- Open browser: http://localhost:6333/dashboard

### 5. Index Your HTML Files

**Single file:**
```powershell
python index.py
```

**Multiple files:**
```powershell
python index_multiple.py
```

### 6. Start Chatting!

**Basic chat:**
```powershell
python chat.py
```

**Enhanced chat with continuous conversation:**
```powershell
python chat_enhanced.py
```

## 📁 File Descriptions

| File | Purpose |
|------|---------|
| `index.py` | Index single HTML file |
| `index_multiple.py` | Index all HTML files in docs/ folder |
| `chat.py` | Simple one-question chat interface |
| `chat_enhanced.py` | Continuous chat with source tracking |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for environment variables |

## 🔧 Key Components

### HTML Loader (BSHTMLLoader)
- Uses BeautifulSoup to parse HTML
- Automatically filters out:
  - JavaScript code
  - CSS styles
  - HTML tags
- Extracts clean, readable text

### Text Splitter
- **Chunk size**: 1000 characters
- **Overlap**: 400 characters
- Ensures context is preserved across chunks

### Embedding Model
- **Model**: `text-embedding-3-large`
- Creates semantic vector representations
- Enables similarity search

### Vector Database
- **Engine**: Qdrant
- **Collection**: `html-rag`
- Stores and retrieves relevant chunks

### LLM
- **Model**: `gpt-4o-mini`
- Generates natural language responses
- Uses retrieved context for accurate answers

## 🎯 Example Queries

Once you've indexed the aircraft spec HTML file, try:

```
❓ What type of aircraft is this?
❓ What are the specifications mentioned?
❓ Tell me about the manufacturer
❓ What is the aircraft's registration number?
❓ Are there any pricing details?
❓ What maintenance information is available?
```

## ⚠️ Troubleshooting

### Issue: Import errors
```
Solution: Make sure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

### Issue: Qdrant connection error
```
Solution: Check if Qdrant is running
docker ps
docker-compose up -d
```

### Issue: "Collection 'html-rag' not found"
```
Solution: Run indexing first
python index.py
```

### Issue: OpenAI API error
```
Solution: Check your .env file has valid OPENAI_API_KEY
```

### Issue: HTML content looks garbled
```
Solution: BSHTMLLoader handles this automatically, but if issues persist:
1. Check HTML file encoding
2. Try adding encoding parameter: open_encoding="utf-8"
```

## 🔄 Re-indexing

To update the index after adding/modifying HTML files:

1. Delete the collection (optional):
   ```python
   from qdrant_client import QdrantClient
   client = QdrantClient(url="http://localhost:6333")
   client.delete_collection("html-rag")
   ```

2. Run indexing again:
   ```powershell
   python index_multiple.py
   ```

## 📊 Comparison with PDF System

| Feature | PDF System (agentic-ai) | HTML System (html-source) |
|---------|------------------------|---------------------------|
| Loader | PyPDFLoader | BSHTMLLoader |
| Metadata | Page numbers | Filename, source path |
| Collection | learning-rag | html-rag |
| Content Filtering | Minimal | Filters scripts/styles |
| Best For | Documents, reports | Web pages, documentation |

## 🎨 Customization

### Change chunk size
Edit `index.py` or `index_multiple.py`:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,    # Smaller chunks
    chunk_overlap=200   # Less overlap
)
```

### Use different embedding model
```python
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small"  # Faster, cheaper
)
```

### Change LLM model
Edit `chat.py`:
```python
response = openai_client.chat.completions.create(
    model="gpt-4o",  # More powerful
    # or
    model="gpt-3.5-turbo",  # Cheaper
    ...
)
```

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OpenAI API Reference](https://platform.openai.com/docs/)


