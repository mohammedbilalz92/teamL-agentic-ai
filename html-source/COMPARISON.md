# Comparison: PDF vs HTML RAG Systems

## Architecture Comparison

### PDF System (agentic-ai/) vs HTML System (html-source/)

| Component | PDF System | HTML System |
|-----------|------------|-------------|
| **Document Loader** | `PyPDFLoader` | `BSHTMLLoader` (BeautifulSoup) |
| **Source Format** | PDF files | HTML files |
| **Content Extraction** | Page-based | DOM-based with script/style filtering |
| **Metadata Tracked** | Page numbers, source path | Filename, source path |
| **Vector Store Collection** | `learning-rag` | `html-rag` |
| **Embedding Model** | `text-embedding-3-large` | `text-embedding-3-large` |
| **LLM Model** | `gpt-4.1-mini` | `gpt-4o-mini` |

## Key Differences

### 1. Content Parsing

**PDF (PyPDFLoader):**
- Extracts text page by page
- Preserves page structure
- Good for: Reports, documents, books
- May include headers/footers repeatedly

```python
loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()
# Returns: List of documents, one per page
```

**HTML (BSHTMLLoader):**
- Parses HTML DOM structure
- Filters out JavaScript and CSS
- Good for: Web pages, documentation, scraped content
- Extracts clean text from markup

```python
loader = BSHTMLLoader(
    file_path=html_path,
    bs_kwargs={"features": "html.parser"}
)
docs = loader.load()
# Returns: Cleaned text content
```

### 2. Metadata Structure

**PDF Metadata:**
```python
{
    'source': 'docs/nodejs.pdf',
    'page_label': '5',
    'page': 4
}
```

**HTML Metadata:**
```python
{
    'source': 'docs/amstat-premier-aircraft-spec-page.html',
    'filename': 'amstat-premier-aircraft-spec-page.html',
    'title': 'Page Title'  # if available
}
```

### 3. Context Formatting

**PDF System:**
```python
context = "\n\n\n".join([
    f"Page Content: {result.page_content}\n"
    f"Page Number: {result.metadata['page_label']}\n"
    f"File Location: {result.metadata['source']}"
    for result in search_results
])
```

**HTML System:**
```python
context = "\n\n".join([
    f"--- Chunk {idx} ---\n"
    f"Content: {result.page_content}\n"
    f"Source File: {result.metadata.get('filename')}\n"
    f"Path: {result.metadata.get('source')}"
    for idx, result in enumerate(search_results, 1)
])
```

### 4. System Prompt Differences

**PDF System:**
```python
SYSTEM_PROMPT = """
You are a helpfull AI Assistant who answeres user query 
based on the available context retrieved from a PDF file 
along with page_contents and page_number.

You should only answer the user based on the following 
context and navigate the user to open the right page 
number to know more.
"""
```

**HTML System:**
```python
SYSTEM_PROMPT = """
You are a helpful AI Assistant who answers user queries 
based on the available context retrieved from an HTML file.

You should only answer the user based on the following 
context extracted from the HTML document.
When answering, be specific and cite which source file 
the information comes from if relevant.
"""
```

## File Structure Comparison

### agentic-ai/ (PDF System)
```
agentic-ai/
├── chat.py              # Single-question chat
├── index.py             # Index single PDF
└── docs/
    └── nodejs.pdf       # Source PDF file
```

### html-source/ (HTML System)
```
html-source/
├── chat.py              # Single-question chat
├── chat_enhanced.py     # Continuous conversation
├── index.py             # Index single HTML file
├── index_multiple.py    # Index all HTML files
├── requirements.txt     # Dependencies
├── env.template         # Environment variable template
├── README.md            # Documentation
├── SETUP_GUIDE.md       # Setup instructions
├── COMPARISON.md        # This file
└── docs/
    └── amstat-premier-aircraft-spec-page.html
```

## When to Use Which System?

### Use PDF System When:
- ✅ Working with PDF documents
- ✅ Page numbers are important (references, citations)
- ✅ Content has clear page-based structure
- ✅ Sources are reports, books, academic papers
- ✅ Need to reference specific pages

### Use HTML System When:
- ✅ Working with web content
- ✅ HTML files from web scraping
- ✅ Online documentation
- ✅ Content has lots of JavaScript/CSS to filter
- ✅ Structure is DOM-based rather than page-based
- ✅ Need to extract clean text from markup

## Advantages of Each System

### PDF System Advantages:
1. **Page Reference**: Easy to cite specific pages
2. **Standard Format**: PDFs are consistent format
3. **Preserved Layout**: Maintains document structure
4. **Universal**: Works with any PDF

### HTML System Advantages:
1. **Clean Extraction**: Automatically removes scripts/styles
2. **Web Native**: Perfect for scraped content
3. **Flexible Parsing**: Can target specific HTML elements
4. **Rich Metadata**: Can extract HTML-specific info (links, headings)
5. **Multiple Files**: Built-in support for batch processing

## Performance Considerations

### Memory Usage:
- **PDF**: Lower (page-by-page processing)
- **HTML**: Can be higher (DOM parsing)

### Processing Speed:
- **PDF**: Fast for simple text PDFs
- **HTML**: Fast with BeautifulSoup, filtering adds slight overhead

### Quality of Extraction:
- **PDF**: Excellent for well-formatted PDFs, poor for scanned/complex PDFs
- **HTML**: Excellent for web content, handles complex markup well

## Extending Both Systems

### Adding Support for More File Types:

```python
# For Word documents
from langchain_community.document_loaders import UnstructuredWordDocumentLoader

# For Markdown
from langchain_community.document_loaders import UnstructuredMarkdownLoader

# For Excel
from langchain_community.document_loaders import UnstructuredExcelLoader
```

### Hybrid Approach:

```python
from pathlib import Path

def load_documents(docs_dir):
    all_docs = []
    
    # Load PDFs
    for pdf in Path(docs_dir).glob("*.pdf"):
        loader = PyPDFLoader(str(pdf))
        all_docs.extend(loader.load())
    
    # Load HTML
    for html in Path(docs_dir).glob("*.html"):
        loader = BSHTMLLoader(str(html))
        all_docs.extend(loader.load())
    
    return all_docs
```

## Best Practices

### For PDF System:
1. Ensure PDFs are text-based (not scanned images)
2. Use OCR for scanned PDFs
3. Clean up headers/footers if repetitive
4. Consider page overlap in chunking

### For HTML System:
1. Inspect HTML quality before indexing
2. Use appropriate BeautifulSoup parser (`html.parser`, `lxml`)
3. Consider custom extraction for complex sites
4. Test with sample queries before full indexing

## Cost Comparison

Both systems use the same models, so costs are similar:

| Operation | Model | Cost per 1M tokens |
|-----------|-------|-------------------|
| Embedding | text-embedding-3-large | $0.13 |
| Chat | gpt-4o-mini | $0.150 (input), $0.600 (output) |

**Tip**: For cost savings, use `text-embedding-3-small` ($0.02/1M tokens)


