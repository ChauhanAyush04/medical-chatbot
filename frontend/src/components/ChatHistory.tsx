import React from 'react';
import { ChatSession } from '@/types';
import '../styles/chat-history.css';

interface ChatHistoryProps {
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  onSelectSession: (session: ChatSession) => void;
  onDeleteSession: (sessionId: string) => void;
  loading: boolean;
}

export const ChatHistory: React.FC<ChatHistoryProps> = ({
  sessions,
  currentSession,
  onSelectSession,
  onDeleteSession,
  loading,
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <aside className="chat-history">
      <h2>Chat History</h2>
      {sessions.length === 0 ? (
        <p className="empty-state">No conversations yet. Start a new chat!</p>
      ) : (
        <ul className="session-list">
          {sessions.map((session) => (
            <li
              key={session.session_id}
              className={`session-item ${currentSession?.session_id === session.session_id ? 'active' : ''}`}
            >
              <button
                className="session-button"
                onClick={() => onSelectSession(session)}
                disabled={loading}
              >
                <div className="session-info">
                  <h3>{session.title}</h3>
                  <p className="session-date">{formatDate(session.updated_at)}</p>
                  <p className="message-count">{session.messages.length} messages</p>
                </div>
              </button>
              <button
                className="delete-btn"
                onClick={() => onDeleteSession(session.session_id)}
                title="Delete"
                disabled={loading}
              >
                🗑️
              </button>
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
};
