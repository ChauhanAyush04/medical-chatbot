export interface ChatMessage {
  id: number;
  user_query: string;
  bot_response: string;
  sources: string;
  created_at: string;
}

export interface ChatSession {
  id: number;
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface MedicalSearchRequest {
  query: string;
  session_id?: string;
}

export interface MedicalSearchResponse {
  query: string;
  answer: string;
  sources: string[];
  confidence_score: number;
}
