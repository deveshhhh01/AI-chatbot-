import axios from 'axios';
import type { SourcesOverview, HealthStatus, SourceReference } from '../types';

const API_BASE = '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Chat non-streaming
  sendMessage: async (message: string, sessionId: string, sourceFilter: string = 'all') => {
    const response = await apiClient.post('/chat', {
      session_id: sessionId,
      message,
      source_filter: sourceFilter,
    });
    return response.data;
  },

  // Chat Streaming (Server-Sent Events)
  streamMessage: async (
    message: string,
    sessionId: string,
    sourceFilter: string = 'all',
    onChunk: (text: string) => void,
    onMetadata: (metadata: { sources: SourceReference[]; retrieved_documents: number; provider: string }) => void,
    onError: (err: any) => void,
    onDone: () => void
  ) => {
    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message,
          source_filter: sourceFilter,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Unable to read stream');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            const jsonStr = trimmed.slice(6);
            try {
              const event = JSON.parse(jsonStr);
              if (event.type === 'metadata') {
                onMetadata({
                  sources: event.sources || [],
                  retrieved_documents: event.retrieved_documents || 0,
                  provider: event.provider || '',
                });
              } else if (event.type === 'chunk') {
                onChunk(event.delta || '');
              } else if (event.type === 'done') {
                onDone();
              } else if (event.type === 'error') {
                onError(new Error(event.message || 'Stream error'));
              }
            } catch (e) {
              console.warn('Error parsing SSE event chunk:', e);
            }
          }
        }
      }
      onDone();
    } catch (err) {
      onError(err);
    }
  },

  // Conversation history
  getChatHistory: async (sessionId: string) => {
    const response = await apiClient.get(`/chat/history/${sessionId}`);
    return response.data;
  },

  // List recent conversations
  getConversations: async () => {
    const response = await apiClient.get('/chat/conversations');
    return response.data;
  },

  // Sources overview
  getSources: async (): Promise<SourcesOverview> => {
    const response = await apiClient.get('/sources');
    return response.data;
  },

  // Health status
  getHealth: async (): Promise<HealthStatus> => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Projects list
  getProjects: async (params: { source?: string; country?: string; city?: string; q?: string; page?: number; page_size?: number } = {}) => {
    const response = await apiClient.get('/projects', { params });
    return response.data;
  },
};
