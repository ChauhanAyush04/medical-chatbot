import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '@/services/api';
import { ChatSession, ChatMessage, MedicalSearchResponse } from '@/types';

export const useChat = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = useCallback(async () => {
    try {
      const data = await apiClient.listSessions();
      setSessions(data);
      // Set first session as current if exists and no current session
      if (data.length > 0 && !currentSession) {
        setCurrentSession(data[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    }
  }, [currentSession]);

  const createNewSession = useCallback(async () => {
    try {
      setLoading(true);
      const session = await apiClient.createSession();
      
      // Refetch sessions from backend to ensure consistency
      await loadSessions();
      
      setCurrentSession(session);
      setError(null);
      return session;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session');
    } finally {
      setLoading(false);
    }
  }, []);

  const sendMessage = useCallback(
    async (query: string) => {
      if (!currentSession) {
        setError('No active session');
        return;
      }

      try {
        setLoading(true);
        setError(null);
        
        const response = await apiClient.searchMedical({
          query,
          session_id: currentSession.session_id,
        });

        // Add message to current session
        const newMessage: ChatMessage = {
          id: currentSession.messages.length + 1,
          user_query: query,
          bot_response: response.answer,
          sources: response.sources.join(', '),
          created_at: new Date().toISOString(),
        };

        const updatedSession = {
          ...currentSession,
          messages: [...currentSession.messages, newMessage],
          updated_at: new Date().toISOString(),
        };

        setCurrentSession(updatedSession);

        // Refetch sessions from backend to update message counts and timestamps in sidebar
        await loadSessions();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to send message');
      } finally {
        setLoading(false);
      }
    },
    [currentSession]
  );

  const deleteSession = useCallback(
    async (sessionId: string) => {
      try {
        await apiClient.deleteSession(sessionId);
        setSessions(sessions.filter((s) => s.session_id !== sessionId));
        if (currentSession?.session_id === sessionId) {
          setCurrentSession(null);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete session');
      }
    },
    [sessions, currentSession]
  );

  return {
    sessions,
    currentSession,
    loading,
    error,
    loadSessions,
    createNewSession,
    setCurrentSession,
    sendMessage,
    deleteSession,
  };
};
