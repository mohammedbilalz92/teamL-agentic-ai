import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface ChatResponse {
  response: string;
  sources?: any[];
  status: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) {}

  sendMessage(message: string, showSources: boolean = true): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/chat`, {
      message: message,
      show_sources: showSources
    });
  }

  search(query: string, topK: number = 5): Observable<any> {
    return this.http.post(`${this.apiUrl}/search`, {
      query: query,
      top_k: topK
    });
  }
}

