# Amstat Chat UI - Angular Application

A modern Angular chat interface for interacting with the Amstat RAG Chat system.

📚 **For complete documentation, see [DOCUMENTATION.md](./DOCUMENTATION.md)**

## Features

- 💬 Real-time chat interface (ChatGPT-like)
- 🔍 RAG-powered responses from vector database
- 📚 Source citations with relevance scores.
- 🎥 **YouTube video embedding with timestamp navigation**
- 🎨 Modern, responsive UI
- ⚡ Fast and efficient
- 📝 Markdown formatting support
- ⌨️ Keyboard shortcuts (Enter to send)

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the Flask API server:**
   ```bash
   cd ../Code
   python api_server.py
   ```

3. **Start the Angular development server:**
   ```bash
   npm start
   ```

4. **Open browser:** Navigate to `http://localhost:4200`

## Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Python Flask API server running (from Code/api_server.py)

## Setup

1. **Install dependencies:**
   ```bash
   cd ChatUI
   npm install
   ```

2. **Start the Flask API server:**
   ```bash
   cd ../Code
   python api_server.py
   ```
   The API will run on http://localhost:5000

3. **Start the Angular development server:**
   ```bash
   cd ChatUI
   npm start
   ```
   The app will be available at http://localhost:4200

## Project Structure

```
ChatUI/
├── src/
│   ├── app/
│   │   ├── app.component.ts      # Main chat component
│   │   ├── app.component.html     # Chat UI template
│   │   ├── app.component.css      # Chat styling
│   │   └── chat.service.ts        # API service
│   ├── index.html
│   ├── main.ts
│   └── styles.css
├── angular.json
├── package.json
└── tsconfig.json
```

## Usage

1. Open http://localhost:4200 in your browser
2. Type your question in the input field
3. Press Enter or click Send
4. View the response with source citations

## API Endpoints

The Angular app connects to:
- `POST http://localhost:5000/api/chat` - Send chat message
- `POST http://localhost:5000/api/search` - Search vector database
- `GET http://localhost:5000/api/health` - Health check

## YouTube Video Features

### Automatic Video Embedding
- When sources contain YouTube URLs, a video player automatically appears at the top
- Single video player for all sources (no duplicates)
- Supports multiple YouTube URL formats

### Timestamp Navigation
- Click on any timestamp (start or end time) to jump to that point in the video
- Video automatically starts playing from the clicked timestamp
- Supports formats: `HH:MM:SS` or `MM:SS`

### Example Usage
1. Ask a question in the chat
2. If sources contain YouTube videos, a video player appears
3. Click any timestamp link (e.g., `00:04:52`) to play from that time
4. Video automatically starts playing

## Documentation

For complete documentation including:
- Detailed feature descriptions
- Technical architecture
- API integration details
- Troubleshooting guide
- Code structure

See **[DOCUMENTATION.md](./DOCUMENTATION.md)**

