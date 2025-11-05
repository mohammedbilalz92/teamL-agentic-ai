# ChatUI - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features Implemented](#features-implemented)
3. [YouTube Video Integration](#youtube-video-integration)
4. [Technical Architecture](#technical-architecture)
5. [Setup Instructions](#setup-instructions)
6. [API Integration](#api-integration)
7. [Code Structure](#code-structure)
8. [Key Components](#key-components)
9. [Troubleshooting](#troubleshooting)
10. [Future Enhancements](#future-enhancements)

---

## Project Overview

The ChatUI is an Angular-based chat interface for interacting with the Amstat RAG (Retrieval-Augmented Generation) Chat system. It provides a modern, ChatGPT-like user experience with enhanced features for displaying source citations and embedded YouTube videos.

### Key Technologies
- **Framework**: Angular 17 (Standalone Components)
- **Language**: TypeScript
- **Styling**: CSS3 with modern design patterns
- **HTTP Client**: Angular HttpClient
- **State Management**: Component-based state

---

## Features Implemented

### 1. **Chat Interface**
- ✅ Real-time chat interface with message history
- ✅ User and assistant message differentiation
- ✅ Loading indicators during API calls
- ✅ Error handling with user-friendly messages
- ✅ Auto-scroll to bottom after new messages
- ✅ Responsive design for mobile and desktop

### 2. **Source Citations**
- ✅ Source list with expandable details section
- ✅ Source metadata display (title, score, timestamps)
- ✅ Relevance score formatting
- ✅ Toggle to show/hide sources

### 3. **YouTube Video Integration** ⭐
- ✅ Automatic video detection from sources
- ✅ Single video player at the top of sources
- ✅ Clickable timestamps for video navigation
- ✅ Automatic playback from selected timestamps
- ✅ Support for multiple YouTube URL formats
- ✅ Responsive video player

### 4. **Markdown Formatting**
- ✅ Bold text (**text**)
- ✅ Italic text (*text*)
- ✅ Inline code (`code`)
- ✅ Code blocks (```code```)
- ✅ Line breaks
- ✅ Lists (numbered and bulleted)
- ✅ HTML escaping for security

### 5. **User Experience**
- ✅ Welcome message on initialization
- ✅ Keyboard shortcuts (Enter to send, Shift+Enter for new line)
- ✅ Disabled input during loading
- ✅ Smooth animations
- ✅ Timestamp formatting
- ✅ Modern, gradient-based UI design

---

## YouTube Video Integration

### Overview
The YouTube video integration allows users to view and interact with videos directly within the chat interface. When sources contain YouTube URLs, a video player is automatically embedded at the top of the sources section.

### Features

#### 1. **Automatic Video Detection**
- Detects YouTube URLs in various formats:
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://www.youtube.com/watch/VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
  - `https://www.youtube.com/embed/VIDEO_ID`
  - `https://www.youtube.com/v/VIDEO_ID`

#### 2. **Single Video Player**
- Only **one video player** is displayed at the top
- If multiple sources share the same video, it shows once
- If sources are from different videos, the first YouTube source's video is used
- All timestamp clicks control this single player

#### 3. **Timestamp Navigation**
- Start and end timestamps are clickable links
- Clicking a timestamp:
  - Updates the video to start from that time
  - Automatically starts playing
  - Works for both start and end timestamps
  - Supports format: `HH:MM:SS` or `MM:SS`

#### 4. **Video Player Features**
- Responsive design (adjusts for mobile/tablet/desktop)
- Fullscreen support
- Autoplay on timestamp click (when user interaction is present)
- Proper iframe permissions for YouTube API
- Error handling with fallback links

### Implementation Details

#### Video Detection Process
1. When sources are received from the API, each source is checked for YouTube URLs
2. The `isYouTubeSource()` method validates the URL format
3. The `extractYouTubeVideoId()` method extracts the video ID using regex patterns
4. If any YouTube source is found, `hasAnyYouTubeSource()` returns true

#### Video Player Display
- Located at the top of the sources section (inside `<details>`)
- Only shown when `hasAnyYouTubeSource(message.sources)` is true
- Uses `getSingleYouTubeEmbedUrl()` to generate the embed URL
- Includes proper sanitization using Angular's `DomSanitizer`

#### Timestamp Clicking
- Timestamps are rendered as clickable links when YouTube sources exist
- Click handler: `playFromTimestamp(timestamp, messageIndex, sourceIndex, source)`
- Process:
  1. Validates the source and extracts video ID
  2. Converts timestamp to seconds
  3. Finds the shared video iframe
  4. Creates new embed URL with `start` parameter and `autoplay=1`
  5. Replaces the iframe to force reload with new timestamp
  6. Sends postMessage command as backup

---

## Technical Architecture

### Component Structure

```
AppComponent (Standalone)
├── Messages Array
├── ChatService (HTTP Client)
├── DomSanitizer (Security)
└── Methods:
    ├── Chat Operations
    ├── YouTube Detection
    ├── Video Embedding
    └── Timestamp Handling
```

### Data Flow

```
User Input → ChatService → Flask API → RAG System → Response
                                                      ↓
                                              Sources Array
                                                      ↓
                                              YouTube Detection
                                                      ↓
                                              Video Embedding
                                                      ↓
                                              Timestamp Links
```

### State Management

- **Messages**: Array of message objects with role, content, sources, timestamp
- **Selected Timestamps**: Map tracking selected timestamps per source
- **Iframe Elements**: Map for quick access to iframe elements
- **Loading State**: Boolean flag for loading indicators

---

## Setup Instructions

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn
- Python Flask API server running (from `../Code/api_server.py`)

### Installation Steps

1. **Install Dependencies**
   ```bash
   cd ChatUI
   npm install
   ```

2. **Start Flask API Server**
   ```bash
   cd ../Code
   python api_server.py
   ```
   The API will run on `http://localhost:5000`

3. **Start Angular Development Server**
   ```bash
   cd ChatUI
   npm start
   ```
   The app will be available at `http://localhost:4200`

### Windows Quick Start
1. Double-click `start_api.bat` to start the API server
2. In terminal: `cd ChatUI && npm start`

---

## API Integration

### Endpoints Used

#### POST `/api/chat`
**Request:**
```json
{
  "message": "user question",
  "show_sources": true
}
```

**Response:**
```json
{
  "response": "AI response text",
  "sources": [
    {
      "id": "source-id",
      "title": "Source Title",
      "topic": "Source Topic",
      "source": "https://www.youtube.com/watch/VIDEO_ID",
      "score": 0.85,
      "timestamp_start": "00:04:52",
      "timestamp_end": "00:06:04",
      "chunk_text": "Source content text"
    }
  ],
  "status": "success"
}
```

### Source Object Structure
- `id`: Unique identifier for the source
- `title`: Title of the source document/video
- `topic`: Topic or subject of the source
- `source`: URL of the source (YouTube URL for videos)
- `score`: Relevance score (0-1)
- `timestamp_start`: Start timestamp (HH:MM:SS format)
- `timestamp_end`: End timestamp (HH:MM:SS format)
- `chunk_text`: Text content from the source

---

## Code Structure

### File Organization

```
ChatUI/
├── src/
│   ├── app/
│   │   ├── app.component.ts          # Main component logic
│   │   ├── app.component.html         # Template
│   │   ├── app.component.css          # Styles
│   │   └── chat.service.ts            # API service
│   ├── index.html                     # Entry HTML
│   ├── main.ts                        # Bootstrap
│   └── styles.css                     # Global styles
├── angular.json                       # Angular configuration
├── package.json                       # Dependencies
├── tsconfig.json                      # TypeScript config
└── README.md                          # Basic documentation
```

### Key Methods in AppComponent

#### Chat Operations
- `sendMessage()`: Handles sending messages to API
- `onKeyPress()`: Keyboard shortcut handling
- `scrollToBottom()`: Auto-scroll functionality

#### YouTube Detection
- `extractYouTubeVideoId(url)`: Extracts video ID from various URL formats
- `isYouTubeSource(source)`: Checks if source is a YouTube video
- `hasAnyYouTubeSource(sources)`: Checks if any source is YouTube
- `getSharedYouTubeSource(sources)`: Gets shared video URL (if all same)
- `getFirstYouTubeSource(sources)`: Gets first YouTube URL

#### Video Embedding
- `getSingleYouTubeEmbedUrl(sources, messageIndex)`: Generates embed URL
- `getSingleYouTubeUrl(sources)`: Gets YouTube URL for external links
- `getYouTubeEmbedUrl(source, messageIndex, sourceIndex)`: Individual embed URL

#### Timestamp Handling
- `playFromTimestamp(timestamp, messageIndex, sourceIndex, source)`: Handles timestamp clicks
- `timestampToSeconds(timestamp)`: Converts timestamp string to seconds
- `formatTimestamp(timestamp)`: Formats Date object for display

#### Message Formatting
- `formatMessage(content)`: Converts markdown to HTML
- `formatTimestamp(timestamp)`: Formats time for display

---

## Key Components

### AppComponent (app.component.ts)

**Main Properties:**
```typescript
messages: Message[]                    // Chat message history
currentMessage: string                 // Current input text
isLoading: boolean                     // Loading state
showSources: boolean                   // Toggle sources visibility
selectedTimestamps: Map<string, string> // Track selected timestamps
iframeElements: Map<string, HTMLIFrameElement> // Track iframes
```

**Main Methods:**
- Chat operations: `sendMessage()`, `onKeyPress()`, `scrollToBottom()`
- YouTube: `extractYouTubeVideoId()`, `isYouTubeSource()`, `hasAnyYouTubeSource()`
- Video: `getSingleYouTubeEmbedUrl()`, `playFromTimestamp()`
- Formatting: `formatMessage()`, `formatTimestamp()`, `timestampToSeconds()`

### ChatService (chat.service.ts)

**Methods:**
- `sendMessage(message, showSources)`: Sends chat message to API
- `search(query, topK)`: Searches vector database

### Message Interface

```typescript
interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
  timestamp: Date;
  loading?: boolean;
}
```

---

## Troubleshooting

### Video Not Playing

**Issue**: YouTube video doesn't appear or doesn't play

**Solutions**:
1. Check browser console for errors (F12)
2. Verify YouTube URL is in correct format
3. Check if `source` field contains YouTube URL
4. Verify video ID extraction is working (check console logs)
5. Ensure iframe permissions are correct
6. Check browser autoplay policies

**Debug Steps**:
- Open browser console
- Look for: "Sources received:", "YouTube sources found:", "Final embed URL:"
- Verify the embed URL is correct
- Check iframe element in DOM inspector

### Timestamps Not Clickable

**Issue**: Timestamps don't respond to clicks

**Solutions**:
1. Verify `hasAnyYouTubeSource()` returns true
2. Check if timestamps have `timestamp-link` class
3. Verify click handler is attached
4. Check console for errors when clicking

### Video Not Starting at Timestamp

**Issue**: Video doesn't start from clicked timestamp

**Solutions**:
1. Check timestamp format (should be HH:MM:SS or MM:SS)
2. Verify `timestampToSeconds()` conversion is correct
3. Check if iframe is being replaced correctly
4. Verify autoplay parameter is in URL
5. Check browser console for postMessage errors

### Sources Not Displaying

**Issue**: Sources section is empty or not visible

**Solutions**:
1. Check `showSources` checkbox is checked
2. Verify API returns sources in response
3. Check browser console for API errors
4. Verify sources array is not empty

### API Connection Issues

**Issue**: Cannot connect to API

**Solutions**:
1. Verify Flask API server is running on port 5000
2. Check CORS settings in Flask API
3. Verify API endpoint URL in `chat.service.ts`
4. Check browser console for CORS errors

---

## Future Enhancements

### Potential Improvements

1. **Video Features**
   - [ ] Video thumbnail previews
   - [ ] Video duration display
   - [ ] Playlist support
   - [ ] Video quality selection
   - [ ] Closed captions support

2. **User Experience**
   - [ ] Message search functionality
   - [ ] Export chat history
   - [ ] Dark mode toggle
   - [ ] Font size adjustment
   - [ ] Keyboard shortcuts panel

3. **Source Management**
   - [ ] Source filtering by type
   - [ ] Source sorting options
   - [ ] Download source content
   - [ ] Share source links
   - [ ] Source bookmarks

4. **Advanced Features**
   - [ ] Multi-language support
   - [ ] Voice input/output
   - [ ] File upload support
   - [ ] Image generation integration
   - [ ] Real-time collaboration

5. **Performance**
   - [ ] Virtual scrolling for long conversations
   - [ ] Lazy loading for sources
   - [ ] Caching strategy
   - [ ] Offline support
   - [ ] Service worker implementation

---

## Configuration

### Environment Variables

Currently, the API URL is hardcoded in `chat.service.ts`:
```typescript
private apiUrl = 'http://localhost:5000/api';
```

To change the API URL, modify this property or use environment files.

### Angular Configuration

- **Port**: Default 4200 (can be changed with `ng serve --port`)
- **Build**: `ng build` for production build
- **Output**: `dist/amstat-chat-ui`

---

## Security Considerations

1. **XSS Protection**: All user content is HTML-escaped before display
2. **URL Sanitization**: YouTube URLs are sanitized using Angular's `DomSanitizer`
3. **CORS**: API server must allow requests from Angular app origin
4. **Content Security Policy**: Consider implementing CSP headers

---

## Browser Compatibility

- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Edge (latest)
- ✅ Safari (latest)
- ⚠️ IE11 (not supported - Angular 17 requires modern browsers)

---

## Performance Notes

- Video iframes are lazy-loaded
- Messages array is managed efficiently
- Change detection is optimized with OnPush strategy (can be implemented)
- Large message histories may need pagination

---

## Support

For issues or questions:
1. Check browser console for errors
2. Review this documentation
3. Check API server logs
4. Verify all dependencies are installed

---

## Version History

### Current Version: 1.0.0

**Features Implemented:**
- ✅ Basic chat interface
- ✅ Source citations
- ✅ YouTube video embedding
- ✅ Timestamp navigation
- ✅ Markdown formatting
- ✅ Responsive design
- ✅ Error handling
- ✅ Loading states

---

## License

This project is part of the Amstat RAG Chat system.

---

**Last Updated**: November 2025
**Documentation Version**: 1.0

