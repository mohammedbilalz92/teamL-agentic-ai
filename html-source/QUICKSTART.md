# 🚀 Quick Start - HTML RAG in 5 Minutes

## Prerequisites Check

- [ ] Python 3.12+ installed
- [ ] Docker installed and running
- [ ] OpenAI API key ready

## Step-by-Step Setup

### Step 1: Activate Virtual Environment (30 seconds)

```powershell
# From E:\Work\camp-hackathon\udemy\
.\agentic-ai\udemy-agentic-ai-venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies (2 minutes)

```powershell
cd html-source
pip install -r requirements.txt
```

### Step 3: Configure API Key (30 seconds)

Create a `.env` file in `html-source/` directory:

```bash
OPENAI_API_KEY=your_api_key_here
```

Or copy from template:
```powershell
copy env.template .env
# Then edit .env with your API key
```

### Step 4: Start Qdrant (1 minute)

```powershell
cd ..
docker-compose up -d
```

Verify at: http://localhost:6333/dashboard

### Step 5: Index HTML Files (30 seconds)

```powershell
cd html-source
python index.py
```

Expected output:
```
Loaded 1 HTML document(s)
Created X chunks from the HTML document
✅ HTML content successfully indexed in Qdrant vector store!
```

### Step 6: Start Chatting! (Now!)

```powershell
python chat_enhanced.py
```

## Test Queries

Try these with the aircraft spec HTML:

```
What is this page about?
Tell me the aircraft specifications
What manufacturer details are mentioned?
```

## What Just Happened?

1. **BSHTMLLoader** parsed your HTML and extracted clean text
2. **RecursiveCharacterTextSplitter** broke it into 1000-char chunks
3. **OpenAI Embeddings** converted chunks to vectors
4. **Qdrant** stored vectors for fast similarity search
5. **GPT-4o-mini** generates answers using retrieved context

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ImportError` | Run `pip install -r requirements.txt` |
| `Connection refused` (Qdrant) | Run `docker-compose up -d` |
| `Collection not found` | Run `python index.py` first |
| `OpenAI API error` | Check your `.env` file has valid key |

## Next Steps

### Add More HTML Files
1. Drop `.html` files into `docs/` folder
2. Run: `python index_multiple.py`
3. Chat with all files!

### Customize Settings

**Change chunk size** (index.py):
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Smaller chunks
    chunk_overlap=100    # Less overlap
)
```

**Change model** (chat.py):
```python
# Cheaper:
model="gpt-3.5-turbo"

# More powerful:
model="gpt-4o"
```

**Retrieve more context** (chat.py):
```python
search_results = vector_db.similarity_search(
    query=user_query, 
    k=10  # Get 10 chunks instead of 4
)
```

## Architecture at a Glance

```
HTML Files → BSHTMLLoader → Text Chunks → OpenAI Embeddings
                                                 ↓
User Query → OpenAI Embeddings → Qdrant Search ← Vector Store
                                        ↓
                              Retrieved Chunks → GPT-4o-mini → Answer
```

## File Guide

| File | Use Case |
|------|----------|
| `index.py` | Index one HTML file |
| `index_multiple.py` | Index all HTML files in docs/ |
| `chat.py` | Simple Q&A |
| `chat_enhanced.py` | Continuous chat with sources |

## Common Commands

```powershell
# Re-index after changes
python index_multiple.py

# Start basic chat
python chat.py

# Start enhanced chat
python chat_enhanced.py

# Check Qdrant status
docker ps

# View Qdrant dashboard
start http://localhost:6333/dashboard
```

## Cost Estimate

For typical usage (100 queries/day):

- **Embedding**: ~$0.01/day
- **Chat**: ~$0.10-0.50/day
- **Total**: ~$5-20/month

## Support

- 📖 Full docs: See `README.md`
- 🔧 Setup details: See `SETUP_GUIDE.md`
- ⚖️ PDF vs HTML: See `COMPARISON.md`

---

**Enjoy your HTML-powered RAG system! 🎉**


