# HTML-Based RAG System

This project implements a Retrieval-Augmented Generation (RAG) system for querying HTML documents using LangChain, OpenAI embeddings, and Qdrant vector database.

## Features

- **HTML Content Parsing**: Uses BeautifulSoup-based loader to extract meaningful text from HTML files
- **Smart Text Chunking**: Splits HTML content into manageable chunks with overlap for better context
- **Vector Search**: Utilizes OpenAI's text-embedding-3-large model for semantic search
- **Conversational AI**: Integrates with GPT-4o-mini for natural language responses

## Prerequisites

- Python 3.12+
- Qdrant vector database running on `http://localhost:6333`
- OpenAI API key

## Setup

1. **Activate Virtual Environment** (if using the one from agentic-ai folder):
   ```bash
   # From the parent directory
   .\agentic-ai\udemy-agentic-ai-venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies**:
   ```bash
   pip install langchain langchain-community langchain-openai langchain-qdrant beautifulsoup4 lxml python-dotenv openai
   ```

3. **Set up Environment Variables**:
   Create a `.env` file in the html-source directory or use the parent directory's .env:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. **Start Qdrant** (using Docker):
   ```bash
   # From parent directory where docker-compose.yml exists
   docker-compose up -d
   ```

## Usage

### Step 1: Index HTML Documents

Run the indexing script to load and process HTML files:

```bash
cd html-source
python index.py
```

This will:
- Load HTML files from the `docs/` folder
- Extract text content (filtering out scripts and styles)
- Split content into chunks
- Create embeddings and store in Qdrant

### Step 2: Chat with Your HTML Content

Once indexed, start the chat interface:

```bash
python chat.py
```

Example queries:
- "What is this page about?"
- "What are the main specifications mentioned?"
- "Tell me about the aircraft details"
- "What information is available about pricing?"

## Key Differences from PDF-Based System

1. **HTML Loader**: Uses `BSHTMLLoader` instead of `PyPDFLoader`
   - Automatically filters out JavaScript, CSS, and non-content elements
   - Extracts clean, readable text from HTML structure

2. **Metadata**: 
   - No page numbers (HTML doesn't have pages)
   - Tracks source file path
   - Can be extended to track HTML sections, headers, or URLs

3. **Collection Name**: Uses `html-rag` instead of `learning-rag` to keep data separate

## File Structure

```
html-source/
├── docs/
│   └── amstat-premier-aircraft-spec-page.html
├── index.py          # Loads and indexes HTML content
├── chat.py           # Interactive chat interface
└── README.md         # This file
```

## Troubleshooting

**Issue**: "Collection not found"
- Solution: Run `index.py` first to create the collection

**Issue**: "Connection refused to Qdrant"
- Solution: Ensure Qdrant is running: `docker-compose up -d`

**Issue**: "OpenAI API error"
- Solution: Check your API key in .env file

## Extending the System

To add more HTML files:
1. Place them in the `docs/` folder
2. Update `html_path` in `index.py` to loop through multiple files
3. Re-run `index.py` to index all files

Example for multiple files:
```python
from pathlib import Path

docs_dir = Path(__file__).parent / "docs"
all_docs = []

for html_file in docs_dir.glob("*.html"):
    loader = BSHTMLLoader(file_path=str(html_file))
    all_docs.extend(loader.load())
```


