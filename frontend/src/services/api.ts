import axios, { AxiosInstance } from 'axios';
import { MedicalSearchRequest, MedicalSearchResponse, ChatSession } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Medical Search
  async searchMedical(request: MedicalSearchRequest): Promise<MedicalSearchResponse> {
    const response = await this.client.post<MedicalSearchResponse>('/medical/search', request);
    return response.data;
  }

  // Chat Sessions
  async createSession(): Promise<ChatSession> {
    const response = await this.client.post<ChatSession>('/chat/sessions');
    return response.data;
  }

  async getSession(sessionId: string): Promise<ChatSession> {
    const response = await this.client.get<ChatSession>(`/chat/sessions/${sessionId}`);
    return response.data;
  }

  async listSessions(): Promise<ChatSession[]> {
    const response = await this.client.get<ChatSession[]>('/chat/sessions');
    return response.data;
  }

  async deleteSession(sessionId: string): Promise<{ message: string }> {
    const response = await this.client.delete<{ message: string }>(`/chat/sessions/${sessionId}`);
    return response.data;
  }
}

export const apiClient = new APIClient();
