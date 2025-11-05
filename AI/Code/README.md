# AI-Enhanced Transcript Chunking Script

This script processes video transcript files using OpenAI to create semantic chunks with meaningful topics, suitable for vector database ingestion.

## Overview

The script processes transcript files from `Input_Files/Vedio_Transcript` and creates:
- **chunks_array.json**: Array format with AI-generated semantic chunks and topics
- **chunks.jsonl**: One JSON object per line (for vector DB ingestion)
- **chunks.json**: Complete structured data with metadata

## Files

- `transcript_chunker_ai.py`: Main AI-enhanced script to process transcript files
- `requirements.txt`: Dependencies (OpenAI library required)

## Usage

### Basic Usage

```bash
python Code/transcript_chunker_ai.py
```

This will:
1. Read all transcript files from `Input_Files/Vedio_Transcript`
2. Use OpenAI (gpt-4.1-mini) to analyze and create semantic chunks
3. Generate meaningful topics (e.g., "Client Share Portal Overview" instead of generic titles)
4. Clean and format text (remove filler words, improve grammar)
5. Create chunks at natural topic boundaries
6. Save chunks in multiple formats
7. Organize output by title in `Processed_Files` folder

### Output Structure

Each processed file creates a folder named after the transcript title:
```
Processed_Files/
  └── Amstat_Premierplus_crash_course/
      ├── chunks_array.json   # Array format (primary output)
      ├── chunks.jsonl        # One chunk per line (for vector DB)
      └── chunks.json         # Complete structured data
```

### Chunk Format

Each chunk in `chunks_array.json` has this structure:
```json
{
  "id": "amstat-premierplus-1",
  "title": "Amstat Premierplus crash course",
  "source": "https://www.youtube.com/watch/...",
  "chunk_text": "The cleaned, well-formatted text content...",
  "metadata": {
    "timestamp_start": "00:00:00",
    "timestamp_end": "00:01:15",
    "topic": "Aircraft Valuation Tool Features"
  }
}
```

## Configuration

The script is configured with:
- **API Key**: Set in the script or via `OPENAI_API_KEY` environment variable
- **Model**: `gpt-4.1-mini` (configurable via `OPENAI_MODEL` environment variable)
- **Chunk Size**: 1000 characters (approximate target, AI prioritizes meaning)
- **Fallback**: Automatically falls back to basic chunking if AI is unavailable

## Features

- ✅ **AI-Powered Semantic Chunking**: Uses OpenAI to analyze transcripts and create meaningful chunks
- ✅ **Intelligent Topic Extraction**: Generates specific topics (e.g., "Client Share Portal Overview") instead of generic titles
- ✅ **Text Cleaning**: Removes filler words, fixes grammar, improves readability
- ✅ **Natural Topic Boundaries**: Breaks at natural topic changes, not arbitrary character limits
- ✅ **Timestamp Tracking**: Preserves start and end timestamps for each chunk
- ✅ **Multiple Output Formats**: JSON array, JSONL, and legacy JSON formats
- ✅ **Organized Output**: Each document in its own folder
- ✅ **Batch Processing**: Processes all files automatically
- ✅ **Automatic Fallback**: Falls back to basic chunking if AI is unavailable

## Requirements

- Python 3.7+
- `openai>=1.0.0` (install with: `pip install openai`)

Install dependencies:
```bash
pip install -r Code/requirements.txt
```

## Vector DB Integration

The JSONL format is optimized for vector database ingestion:

1. **OpenAI**: Can directly read JSONL files
2. **Pinecone**: Import JSONL format
3. **Weaviate**: Supports JSONL ingestion
4. **ChromaDB**: Can load from JSONL

### Example: Loading into Vector DB

```python
import json

# Read chunks from JSONL
chunks = []
with open('Processed_Files/Amstat_Premierplus_crash_course/chunks.jsonl', 'r') as f:
    for line in f:
        chunk = json.loads(line)
        chunks.append(chunk)

# Or read from array format
with open('Processed_Files/Amstat_Premierplus_crash_course/chunks_array.json', 'r') as f:
    chunks = json.load(f)

# Each chunk has:
# - id: Unique identifier (e.g., "amstat-premierplus-1")
# - title: Document title
# - source: Source URL
# - chunk_text: Text content for embedding
# - metadata: timestamp_start, timestamp_end, topic
```

## Notes

- The script uses OpenAI API which requires an API key
- If AI analysis fails, it automatically falls back to basic chunking
- Chunks are created at semantic boundaries, not fixed character limits
- Topics are AI-generated and descriptive, not just the video title
