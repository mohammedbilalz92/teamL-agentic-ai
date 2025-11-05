"""
AI-Enhanced Transcript Chunking Script
Uses OpenAI to analyze transcripts and create meaningful semantic chunks.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not installed. Install with: pip install openai")


class AITranscriptChunker:
    """Processes transcript files using OpenAI to create semantic chunks."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, 
                 openai_api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the AI chunker.
        
        Args:
            chunk_size: Approximate target size for chunks (used as guidance)
            chunk_overlap: Overlap between chunks
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: OpenAI model to use
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model = model
        
        # Initialize OpenAI client
        if OPENAI_AVAILABLE:
            api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.use_ai = True
            else:
                print("Warning: OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
                self.client = None
                self.use_ai = False
        else:
            self.client = None
            self.use_ai = False
    
    def extract_title_from_filename(self, filename: str) -> str:
        """Extract title from transcript filename."""
        title = filename.replace('tactiq-free-transcript-', '')
        title = title.replace('.txt', '')
        title = title.replace('_', ' ')
        return title
    
    def parse_transcript(self, file_path: str) -> Dict[str, Any]:
        """
        Parse transcript file and extract metadata, text, and timestamps.
        
        Returns:
            Dictionary with metadata and segments with timestamps
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        metadata = {
            'source_file': os.path.basename(file_path),
            'title': self.extract_title_from_filename(os.path.basename(file_path)),
            'url': None,
            'processed_date': datetime.now().isoformat()
        }
        
        # Store segments with their timestamps
        segments = []  # List of (timestamp, text) tuples
        timestamp_pattern = re.compile(r'^(\d{2}:\d{2}:\d{2})\.\d{3}\s+(.+)$')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Extract URL
            if line.startswith('# https://'):
                metadata['url'] = line.replace('# ', '')
                continue
            
            # Extract transcript lines (with timestamps)
            match = timestamp_pattern.match(line)
            if match:
                timestamp = match.group(1)  # HH:MM:SS format
                text = match.group(2)
                segments.append((timestamp, text))
        
        return {
            'metadata': metadata,
            'segments': segments
        }
    
    def create_slug_from_title(self, title: str) -> str:
        """Create a URL-friendly slug from title."""
        slug = title.lower()
        common_words = {'how', 'many', 'can', 'i', 'share', 'a', 'an', 'the', 'with', 
                       'what', 'does', 'is', 'are', 'do', 'you', 'your', 'my', 'me', 
                       'we', 'to', 'for', 'of', 'in', 'on', 'at', 'by'}
        words = re.findall(r'\b\w+\b', slug)
        meaningful_words = [w for w in words if w not in common_words and len(w) > 2]
        
        if meaningful_words:
            key_words = meaningful_words[:2] if len(meaningful_words) >= 2 else meaningful_words
            slug = '-'.join(key_words)
        else:
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[-\s]+', '-', slug)
            words = slug.split('-')
            if len(words) > 3:
                slug = '-'.join(words[:3])
        
        if not slug.startswith('amstat-'):
            slug = f"amstat-{slug}"
        
        return slug
    
    def analyze_with_openai(self, segments: List[tuple], metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use OpenAI to analyze transcript and create semantic chunks.
        
        Args:
            segments: List of (timestamp, text) tuples
            metadata: Document metadata
            
        Returns:
            List of chunk dictionaries with AI-generated topics
        """
        if not self.use_ai or not self.client:
            raise ValueError("OpenAI client not initialized. Provide API key.")
        
        # Combine segments into text with timestamps
        transcript_parts = []
        for timestamp, text in segments:
            transcript_parts.append(f"[{timestamp}] {text}")
        
        full_transcript = "\n".join(transcript_parts)
        
        # Create prompt for OpenAI
        prompt = f"""Analyze the following video transcript and break it into meaningful semantic chunks. Each chunk should:
1. Represent a complete thought, topic, or concept
2. Have a clear, descriptive topic name (NOT the video title - be specific, e.g., "Client Share Portal Overview", "Managing Licenses", "Aircraft Valuation Tool Features")
3. Include accurate start and end timestamps from the transcript
4. Be comprehensive but focused (aim for {self.chunk_size} characters per chunk, but prioritize meaning over length)

Video Title: {metadata['title']}
Source URL: {metadata.get('url', 'N/A')}

TRANSCRIPT (format: [timestamp] text):
{full_transcript}

Return a JSON object with a "chunks" array. Each chunk in the array should have this exact structure:
{{
  "chunk_text": "The cleaned, well-formatted text content. Remove filler words like 'um', 'uh', 'like' where appropriate. Fix grammar and make it readable.",
  "timestamp_start": "HH:MM:SS",
  "timestamp_end": "HH:MM:SS",
  "topic": "A specific, descriptive topic name for this chunk (e.g., 'Client Share Portal Overview', 'Managing and Increasing Licenses', NOT the video title)"
}}

CRITICAL REQUIREMENTS:
- Create meaningful breaks at natural topic boundaries (when the speaker moves to a new topic)
- Each topic must be specific and descriptive (e.g., "Aircraft Valuation Tool Features" NOT "Premier Plus Overview")
- Clean up the text: remove excessive filler words, fix grammar, make it professional
- Use timestamps from the transcript - start timestamp should match the first segment in the chunk, end timestamp should match the last segment
- Break at natural pauses or topic changes, not arbitrary character limits
- Ensure timestamps are accurate and sequential
- Return ONLY valid JSON with a "chunks" array

Return your response as a JSON object with a "chunks" key containing the array:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing video transcripts and creating meaningful, semantic chunks. You identify natural topic boundaries and create descriptive topics. Always return valid JSON with a 'chunks' array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            # Handle different response formats
            if isinstance(result, list):
                ai_chunks = result
            elif isinstance(result, dict) and 'chunks' in result:
                ai_chunks = result['chunks']
            elif isinstance(result, dict) and 'items' in result:
                ai_chunks = result['items']
            elif isinstance(result, dict):
                # Try to extract array from any key
                for key in ['chunks', 'items', 'data', 'results']:
                    if key in result and isinstance(result[key], list):
                        ai_chunks = result[key]
                        break
                else:
                    # Last resort: use first list value
                    ai_chunks = [v for v in result.values() if isinstance(v, list)]
                    ai_chunks = ai_chunks[0] if ai_chunks else []
            else:
                raise ValueError("Unexpected response format from OpenAI")
            
            if not isinstance(ai_chunks, list) or len(ai_chunks) == 0:
                raise ValueError("No chunks returned from OpenAI")
            
            # Format chunks to match our structure
            title_slug = self.create_slug_from_title(metadata['title'])
            formatted_chunks = []
            
            for idx, chunk in enumerate(ai_chunks, 1):
                # Clean and validate chunk data
                chunk_text = chunk.get('chunk_text', chunk.get('text', '')).strip()
                if not chunk_text:
                    continue  # Skip empty chunks
                
                # Validate timestamps
                timestamp_start = chunk.get('timestamp_start', '00:00:00')
                timestamp_end = chunk.get('timestamp_end', '00:00:00')
                
                # Ensure timestamp format is HH:MM:SS
                if len(timestamp_start.split(':')) == 2:
                    timestamp_start = f"00:{timestamp_start}"
                if len(timestamp_end.split(':')) == 2:
                    timestamp_end = f"00:{timestamp_end}"
                
                formatted_chunk = {
                    'id': f"{title_slug}-{idx}",
                    'title': metadata['title'],
                    'source': metadata.get('url', ''),
                    'chunk_text': chunk_text,
                    'metadata': {
                        'timestamp_start': timestamp_start,
                        'timestamp_end': timestamp_end,
                        'topic': chunk.get('topic', metadata['title'])
                    }
                }
                formatted_chunks.append(formatted_chunk)
            
            return formatted_chunks
            
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def create_chunks_fallback(self, segments: List[tuple], metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fallback chunking method when AI is not available.
        Uses basic chunking with timestamp tracking.
        """
        if not segments:
            return []
        
        # Combine segments into text
        full_text_parts = []
        timestamp_map = []
        
        for timestamp, text in segments:
            full_text_parts.append(text)
            start_pos = sum(len(part) + 1 for part in full_text_parts[:-1])
            for i in range(len(text)):
                timestamp_map.append((start_pos + i, timestamp))
        
        full_text = ' '.join(full_text_parts)
        title_slug = self.create_slug_from_title(metadata['title'])
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(full_text):
            end = start + self.chunk_size
            chunk_text = full_text[start:end]
            
            if end < len(full_text):
                last_space = chunk_text.rfind(' ')
                if last_space > self.chunk_size * 0.5:
                    chunk_text = chunk_text[:last_space]
                    end = start + last_space
            
            # Find timestamps
            chunk_start_timestamp = None
            chunk_end_timestamp = None
            
            for pos, ts in timestamp_map:
                if pos >= start and chunk_start_timestamp is None:
                    chunk_start_timestamp = ts
                    break
            
            for pos, ts in reversed(timestamp_map):
                if pos <= end:
                    chunk_end_timestamp = ts
                    break
            
            if chunk_start_timestamp is None and segments:
                chunk_start_timestamp = segments[0][0]
            if chunk_end_timestamp is None and segments:
                chunk_end_timestamp = segments[-1][0]
            
            chunk = {
                'id': f"{title_slug}-{chunk_index + 1}",
                'title': metadata['title'],
                'source': metadata.get('url', ''),
                'chunk_text': chunk_text.strip(),
                'metadata': {
                    'timestamp_start': chunk_start_timestamp or '00:00:00',
                    'timestamp_end': chunk_end_timestamp or '00:00:00',
                    'topic': metadata['title']
                }
            }
            
            chunks.append(chunk)
            start = end - self.chunk_overlap
            chunk_index += 1
            
            if start >= end:
                start = end
        
        return chunks
    
    def process_file(self, input_file_path: str, output_dir: str, use_ai: bool = True) -> str:
        """
        Process a single transcript file and save chunks.
        
        Args:
            input_file_path: Path to input transcript file
            output_dir: Directory to save processed chunks
            use_ai: Whether to use OpenAI for analysis (default: True)
        """
        # Parse transcript
        parsed_data = self.parse_transcript(input_file_path)
        
        # Create chunks
        if use_ai and self.use_ai:
            try:
                print(f"  -> Using AI to analyze transcript...")
                chunks = self.analyze_with_openai(parsed_data['segments'], parsed_data['metadata'])
            except Exception as e:
                print(f"  -> AI analysis failed: {str(e)}")
                print(f"  -> Falling back to basic chunking...")
                chunks = self.create_chunks_fallback(parsed_data['segments'], parsed_data['metadata'])
        else:
            chunks = self.create_chunks_fallback(parsed_data['segments'], parsed_data['metadata'])
        
        # Create output directory
        title = parsed_data['metadata']['title']
        safe_folder_name = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        file_output_dir = os.path.join(output_dir, safe_folder_name)
        os.makedirs(file_output_dir, exist_ok=True)
        
        # Save as array format (primary output)
        array_file = os.path.join(file_output_dir, 'chunks_array.json')
        with open(array_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        # Save as JSONL (for vector DB)
        jsonl_file = os.path.join(file_output_dir, 'chunks.jsonl')
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        # Save legacy format
        output_data = {
            'source_file': parsed_data['metadata']['source_file'],
            'title': title,
            'url': parsed_data['metadata']['url'],
            'total_chunks': len(chunks),
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'processed_date': parsed_data['metadata']['processed_date'],
            'chunks': chunks
        }
        output_file = os.path.join(file_output_dir, 'chunks.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Processed: {parsed_data['metadata']['source_file']}")
        print(f"  -> Created {len(chunks)} chunks")
        print(f"  -> Saved Array JSON: {file_output_dir}/chunks_array.json")
        print(f"  -> Saved JSONL: {file_output_dir}/chunks.jsonl")
        
        return array_file
    
    def process_all_files(self, input_dir: str, output_dir: str, use_ai: bool = True):
        """
        Process all transcript files in the input directory.
        
        Args:
            input_dir: Directory containing transcript files
            output_dir: Directory to save processed chunks
            use_ai: Whether to use OpenAI for analysis
        """
        os.makedirs(output_dir, exist_ok=True)
        
        transcript_files = list(Path(input_dir).glob('tactiq-free-transcript-*.txt'))
        
        if not transcript_files:
            print(f"No transcript files found in {input_dir}")
            return
        
        print(f"Found {len(transcript_files)} transcript file(s)")
        if use_ai and self.use_ai:
            print(f"Using OpenAI model: {self.model}")
        print()
        
        processed_files = []
        for file_path in transcript_files:
            try:
                output_file = self.process_file(str(file_path), output_dir, use_ai=use_ai)
                processed_files.append(output_file)
            except Exception as e:
                print(f"[ERROR] Error processing {file_path.name}: {str(e)}")
        
        print(f"\n{'='*60}")
        print(f"Processing complete!")
        print(f"Total files processed: {len(processed_files)}")
        print(f"Output directory: {output_dir}")


def main():
    """Main function to run the AI-enhanced chunking process."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Configuration
    INPUT_DIR = os.path.join(project_root, 'Input_Files', 'Vedio_Transcript')
    OUTPUT_DIR = os.path.join(project_root, 'Processed_Files')
    
    # OpenAI configuration
    # Use provided API key or environment variable
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') 
    # Use gpt-4.1-mini as specified by user
    MODEL = os.getenv('OPENAI_MODEL', "gpt-4.1-mini")
    
    print(f"Using OpenAI model: {MODEL}")
    print(f"API Key: {'*' * 20}...{OPENAI_API_KEY[-4:] if OPENAI_API_KEY else 'NOT SET'}\n")
    
    # Initialize chunker
    chunker = AITranscriptChunker(
        chunk_size=1000,
        chunk_overlap=200,
        openai_api_key=OPENAI_API_KEY,
        model=MODEL
    )
    
    # Process all files with AI
    use_ai = chunker.use_ai
    if not use_ai:
        print("Note: OpenAI API key not found. Using basic chunking.")
        print("Set OPENAI_API_KEY environment variable to enable AI analysis.\n")
    else:
        print("AI-enhanced chunking enabled!\n")
    
    chunker.process_all_files(INPUT_DIR, OUTPUT_DIR, use_ai=use_ai)


if __name__ == '__main__':
    main()

