import { Component, OnInit } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from './chat.service';
import { firstValueFrom } from 'rxjs';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
  timestamp: Date;
  loading?: boolean;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, DecimalPipe],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  messages: Message[] = [];
  currentMessage: string = '';
  isLoading: boolean = false;
  showSources: boolean = true;
  // Track selected timestamp for each source (key: source index in message, value: timestamp)
  selectedTimestamps: Map<string, string> = new Map();
  // Track iframe elements for quick access
  private iframeElements: Map<string, HTMLIFrameElement> = new Map();

  constructor(
    private chatService: ChatService,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit() {
    // Add welcome message
    this.messages.push({
      role: 'assistant',
      content: 'Hello! I\'m your Amstat RAG Assistant. I can help you with questions about Amstat features, functionality, and documentation. How can I assist you today?',
      timestamp: new Date()
    });
  }

  async sendMessage() {
    if (!this.currentMessage.trim() || this.isLoading) {
      return;
    }

    const userMessage = this.currentMessage.trim();
    this.currentMessage = '';

    // Add user message
    this.messages.push({
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    });

    // Add loading message
    const loadingMessage: Message = {
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      loading: true
    };
    this.messages.push(loadingMessage);
    this.isLoading = true;

    try {
      // Call API
      const response = await firstValueFrom(this.chatService.sendMessage(userMessage, this.showSources));
      
      // Remove loading message
      this.messages.pop();
      
      // Add assistant response
      const assistantMessage = {
        role: 'assistant' as const,
        content: response.response,
        sources: response.sources || [],
        timestamp: new Date()
      };
      
      // Debug: Log sources to check YouTube URLs
      if (assistantMessage.sources && assistantMessage.sources.length > 0) {
        console.log('Sources received:', assistantMessage.sources);
        const youtubeSources = assistantMessage.sources.filter(s => this.isYouTubeSource(s));
        console.log('YouTube sources found:', youtubeSources.length);
        if (youtubeSources.length > 0) {
          console.log('First YouTube source:', youtubeSources[0]);
          const videoUrl = this.getFirstYouTubeSource(assistantMessage.sources);
          console.log('Video URL to embed:', videoUrl);
        }
      }
      
      this.messages.push(assistantMessage);
    } catch (error: any) {
      // Remove loading message
      this.messages.pop();
      
      // Add error message
      this.messages.push({
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message || 'Unknown error'}. Please try again.`,
        timestamp: new Date()
      });
    } finally {
      this.isLoading = false;
      // Scroll to bottom
      setTimeout(() => this.scrollToBottom(), 100);
    }
  }

  async onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      await this.sendMessage();
    }
  }

  scrollToBottom() {
    const chatContainer = document.querySelector('.chat-messages');
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  formatTimestamp(timestamp: Date): string {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  /**
   * Extract YouTube video ID from various YouTube URL formats
   */
  extractYouTubeVideoId(url: string): string | null {
    if (!url) return null;
    
    // Match various YouTube URL formats
    const patterns = [
      // Standard format: youtube.com/watch?v=VIDEO_ID
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#\/]+)/,
      // Format with other params: youtube.com/watch?param=value&v=VIDEO_ID
      /youtube\.com\/watch\?.*[&?]v=([^&\n?#\/]+)/,
      // Format: youtube.com/watch/VIDEO_ID (without ?v=) - this is the format we're seeing
      /youtube\.com\/watch\/([^&\n?#\/\s]+)/,
      // Format: youtube.com/v/VIDEO_ID
      /youtube\.com\/v\/([^&\n?#\/]+)/,
      // Short format: youtu.be/VIDEO_ID
      /youtu\.be\/([^&\n?#\/]+)/
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match && match[1]) {
        const videoId = match[1];
        // Validate video ID (should be alphanumeric, dashes, underscores)
        if (/^[a-zA-Z0-9_-]+$/.test(videoId)) {
          return videoId;
        }
      }
    }
    
    return null;
  }

  /**
   * Check if a source is a YouTube video
   */
  isYouTubeSource(source: any): boolean {
    if (!source) return false;
    // Check multiple possible URL fields
    const url = source.source || source.url || source.video_url || source.link;
    if (!url) {
      return false;
    }
    
    const videoId = this.extractYouTubeVideoId(url);
    const isYouTube = videoId !== null;
    
    return isYouTube;
  }

  /**
   * Get YouTube embed URL with timestamp support
   */
  getYouTubeEmbedUrl(source: any, messageIndex: number, sourceIndex: number): SafeResourceUrl | null {
    // Check multiple possible URL fields
    const url = source.source || source.url || source.video_url || source.link;
    if (!url) return null;
    
    const videoId = this.extractYouTubeVideoId(url);
    if (!videoId) return null;

    const key = `${messageIndex}-${sourceIndex}`;
    let timestamp = source.timestamp_start;
    
    // Use selected timestamp if available
    if (this.selectedTimestamps.has(key)) {
      timestamp = this.selectedTimestamps.get(key);
    }

    let embedUrl = `https://www.youtube.com/embed/${videoId}`;
    
    // Add timestamp if available
    if (timestamp) {
      const seconds = this.timestampToSeconds(timestamp);
      if (seconds > 0) {
        embedUrl += `?start=${seconds}`;
      }
    }
    
    return this.sanitizer.bypassSecurityTrustResourceUrl(embedUrl);
  }

  /**
   * Update video to play from a specific timestamp
   */
  playFromTimestamp(timestamp: string, messageIndex: number, sourceIndex: number, source: any): void {
    // Check if source is YouTube or if there's any YouTube source
    const sources = this.messages[messageIndex]?.sources || [];
    const hasAnyYouTube = this.hasAnyYouTubeSource(sources);
    
    if (!hasAnyYouTube) {
      console.warn('No YouTube sources found');
      return;
    }
    
    // Get the video URL - use the clicked source's URL if it's YouTube, otherwise use the first YouTube source
    let url: string | null = null;
    if (this.isYouTubeSource(source)) {
      url = source.source || source.url || source.video_url || source.link;
    } else {
      // If clicked source is not YouTube, use the first YouTube source from the list
      url = this.getFirstYouTubeSource(sources);
    }
    
    if (!url) {
      console.warn('Could not find YouTube URL');
      return;
    }
    
    const videoId = this.extractYouTubeVideoId(url);
    if (!videoId) {
      console.warn('Could not extract video ID from URL:', url);
      return;
    }
    
    const seconds = this.timestampToSeconds(timestamp);
    if (seconds < 0) {
      console.warn('Invalid timestamp:', timestamp);
      return;
    }
    
    console.log('Playing video from timestamp:', timestamp, '(', seconds, 'seconds)');
    
    // Always use the shared/single video player at the top
    const sharedKey = `${messageIndex}-shared`;
    let iframe = document.querySelector(`iframe[data-source-key="${sharedKey}"]`) as HTMLIFrameElement;
    
    if (!iframe) {
      console.warn('Could not find shared video iframe with key:', sharedKey);
      return;
    }
    
    const iframeKey = sharedKey;
    
    // Store the timestamp
    this.selectedTimestamps.set(iframeKey, timestamp);
    
    // Create new embed URL with timestamp and autoplay
    // Use origin parameter for proper postMessage communication
    const embedUrl = `https://www.youtube.com/embed/${videoId}?start=${seconds}&autoplay=1&enablejsapi=1&origin=${encodeURIComponent(window.location.origin)}&rel=0`;
    
    // Always replace the iframe to ensure it starts from the correct timestamp
    // This is the most reliable method
    const parent = iframe.parentElement;
    if (!parent) {
      console.error('Could not find parent element for iframe');
      return;
    }
    
    // Create a new iframe with the updated URL
    const newIframe = document.createElement('iframe');
    newIframe.src = embedUrl;
    newIframe.setAttribute('data-source-key', iframe.getAttribute('data-source-key') || iframeKey);
    newIframe.setAttribute('id', iframe.getAttribute('id') || '');
    newIframe.frameBorder = '0';
    newIframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    newIframe.allowFullscreen = true;
    newIframe.className = 'youtube-embed';
    
    // Copy styles from existing iframe
    const computedStyle = window.getComputedStyle(iframe);
    newIframe.style.width = computedStyle.width || '100%';
    newIframe.style.height = computedStyle.height || '315px';
    newIframe.style.maxWidth = computedStyle.maxWidth || '560px';
    newIframe.style.borderRadius = computedStyle.borderRadius || '0.5rem';
    newIframe.style.marginTop = computedStyle.marginTop || '0.5rem';
    
    // Replace the old iframe with the new one
    parent.replaceChild(newIframe, iframe);
    
    // Update our reference
    this.iframeElements.set(iframeKey, newIframe);
    
    console.log('Iframe replaced successfully. Video should start playing from:', timestamp, '(', seconds, 'seconds)');
    
    // As a backup, try to send play command after a short delay
    // This helps in case autoplay is blocked by browser
    setTimeout(() => {
      try {
        newIframe.contentWindow?.postMessage(JSON.stringify({
          event: 'command',
          func: 'playVideo',
          args: []
        }), 'https://www.youtube.com');
      } catch (e) {
        // This is expected if autoplay works automatically
        console.log('PostMessage play command (backup):', e);
      }
    }, 1000);
  }

  /**
   * Get the source URL for external links
   */
  getSourceUrl(source: any): string {
    return source.source || source.url || source.video_url || source.link || '#';
  }

  /**
   * Check if all sources share the same YouTube video URL
   */
  getSharedYouTubeSource(sources: any[]): string | null {
    if (!sources || sources.length === 0) return null;
    
    // Get all YouTube URLs from sources
    const youtubeUrls = sources
      .map(s => s.source || s.url || s.video_url || s.link)
      .filter(url => url && this.extractYouTubeVideoId(url) !== null);
    
    if (youtubeUrls.length === 0) return null;
    
    // Check if all YouTube URLs are the same (same video ID)
    const firstVideoId = this.extractYouTubeVideoId(youtubeUrls[0]);
    const allSame = youtubeUrls.every(url => 
      this.extractYouTubeVideoId(url) === firstVideoId
    );
    
    return allSame ? youtubeUrls[0] : null;
  }

  /**
   * Get the first YouTube source URL from any source (for single video player)
   */
  getFirstYouTubeSource(sources: any[]): string | null {
    if (!sources || sources.length === 0) return null;
    
    // Find the first source that has a YouTube URL
    for (const source of sources) {
      const url = source.source || source.url || source.video_url || source.link;
      if (url && this.extractYouTubeVideoId(url) !== null) {
        return url;
      }
    }
    
    return null;
  }

  /**
   * Check if any sources are YouTube videos
   */
  hasAnyYouTubeSource(sources: any[]): boolean {
    if (!sources || sources.length === 0) return false;
    return sources.some(s => this.isYouTubeSource(s));
  }

  /**
   * Get shared YouTube embed URL (for when all sources are from the same video)
   */
  getSharedYouTubeEmbedUrl(sources: any[], messageIndex: number): SafeResourceUrl | null {
    const sharedUrl = this.getSharedYouTubeSource(sources);
    if (!sharedUrl) return null;
    
    const videoId = this.extractYouTubeVideoId(sharedUrl);
    if (!videoId) return null;
    
    // Use the first source's timestamp_start as default
    const firstSource = sources.find(s => this.isYouTubeSource(s));
    const timestamp = firstSource?.timestamp_start || '';
    
    let embedUrl = `https://www.youtube.com/embed/${videoId}`;
    
    if (timestamp) {
      const seconds = this.timestampToSeconds(timestamp);
      if (seconds > 0) {
        embedUrl += `?start=${seconds}`;
      }
    }
    
    return this.sanitizer.bypassSecurityTrustResourceUrl(embedUrl);
  }

  /**
   * Get single YouTube embed URL (for when showing one video at top)
   */
  getSingleYouTubeEmbedUrl(sources: any[], messageIndex: number): SafeResourceUrl | null {
    // Try shared URL first, then fall back to first YouTube source
    const url = this.getSharedYouTubeSource(sources) || this.getFirstYouTubeSource(sources);
    if (!url) {
      console.warn('No YouTube URL found in sources');
      return null;
    }
    
    const videoId = this.extractYouTubeVideoId(url);
    if (!videoId) {
      console.warn('Could not extract video ID from URL:', url);
      return null;
    }
    
    console.log('Creating YouTube embed URL for video ID:', videoId);
    
    // Use the first source's timestamp_start as default
    const firstSource = sources.find(s => this.isYouTubeSource(s));
    const timestamp = firstSource?.timestamp_start || '';
    
    // Build embed URL with proper parameters
    let embedUrl = `https://www.youtube.com/embed/${videoId}?enablejsapi=1&origin=${encodeURIComponent(window.location.origin)}&rel=0`;
    
    if (timestamp) {
      const seconds = this.timestampToSeconds(timestamp);
      if (seconds > 0) {
        embedUrl += `&start=${seconds}`;
      }
    }
    
    console.log('Final embed URL:', embedUrl);
    const safeUrl = this.sanitizer.bypassSecurityTrustResourceUrl(embedUrl);
    return safeUrl;
  }

  /**
   * Get the YouTube URL for the single video player
   */
  getSingleYouTubeUrl(sources: any[]): string | null {
    return this.getSharedYouTubeSource(sources) || this.getFirstYouTubeSource(sources);
  }

  /**
   * Convert timestamp string (HH:MM:SS or MM:SS) to seconds
   */
  timestampToSeconds(timestamp: string): number {
    if (!timestamp) return 0;
    
    // Remove any whitespace
    timestamp = timestamp.trim();
    
    // Handle format like "00:04:52" or "04:52"
    const parts = timestamp.split(':').map(Number);
    
    // Validate all parts are numbers
    if (parts.some(isNaN)) {
      console.warn('Invalid timestamp format:', timestamp);
      return 0;
    }
    
    if (parts.length === 3) {
      // HH:MM:SS
      const totalSeconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
      return totalSeconds;
    } else if (parts.length === 2) {
      // MM:SS
      const totalSeconds = parts[0] * 60 + parts[1];
      return totalSeconds;
    }
    
    console.warn('Unexpected timestamp format:', timestamp);
    return 0;
  }

  formatMessage(content: string): string {
    // Format text similar to ChatGPT - preserve line breaks and basic formatting
    if (!content) return '';
    
    // Escape HTML to prevent XSS
    let formatted = content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    
    // Convert code blocks first (before other formatting)
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    // Protect inline code blocks temporarily
    const codePlaceholders: string[] = [];
    formatted = formatted.replace(/`([^`]+)`/g, (match, code) => {
      const placeholder = `___INLINE_CODE_${codePlaceholders.length}___`;
      codePlaceholders.push(code);
      return placeholder;
    });
    
    // Convert bold: **text** or __text__
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>');
    
    // Convert italic: *text* (single asterisk, not part of **)
    formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Restore inline code blocks
    codePlaceholders.forEach((code, index) => {
      formatted = formatted.replace(`___INLINE_CODE_${index}___`, '<code>' + code + '</code>');
    });
    
    // Convert line breaks to <br>
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Convert lists
    const lines = formatted.split('<br>');
    const processedLines: string[] = [];
    let inList = false;
    
    for (let line of lines) {
      const listMatch = line.match(/^(\d+\.\s+|[-*]\s+)(.+)$/);
      if (listMatch) {
        if (!inList) {
          processedLines.push('<ul>');
          inList = true;
        }
        processedLines.push(`<li>${listMatch[2]}</li>`);
      } else {
        if (inList) {
          processedLines.push('</ul>');
          inList = false;
        }
        if (line.trim()) {
          processedLines.push(`<p>${line}</p>`);
        }
      }
    }
    
    if (inList) {
      processedLines.push('</ul>');
    }
    
    return processedLines.join('');
  }
}

