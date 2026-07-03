import React, { useState, useEffect, useRef } from 'react';
import { ChatSession } from '@/types';
import '../styles/chatbox.css';

interface ChatBoxProps {
  session: ChatSession | null;
  onSendMessage: (message: string) => Promise<void>;
  loading: boolean;
  error: string | null;
}

export const ChatBox: React.FC<ChatBoxProps> = ({ session, onSendMessage, loading, error }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [session?.messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const message = input.trim();
    setInput('');
    await onSendMessage(message);
  };

  if (!session) {
    return (
      <div className="chatbox empty">
        <div className="empty-state-large">
          <h2>🏥 Welcome to Medical ChatBot</h2>
          <p>Start a new conversation to ask medical questions</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chatbox">
      <div className="disclaimer">
        <p>⚠️ This bot provides general educational information only. Always consult a healthcare provider for medical advice.</p>
      </div>

      <div className="messages">
        {session.messages.length === 0 ? (
          <div className="empty-messages">
            <p>No messages yet. Ask a medical question!</p>
          </div>
        ) : (
          session.messages.map((msg, idx) => (
            <div key={idx} className="message-group">
              <div className="user-message">
                <p>{msg.user_query}</p>
              </div>
              <div className="bot-message">
                <p>{msg.bot_response}</p>
                {msg.sources && (
                  <div className="sources">
                    <strong>📚 Sources:</strong> {msg.sources}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Thinking...</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask a medical question..."
          disabled={loading}
          className="message-input"
        />
        <button onClick={handleSend} disabled={loading} className="send-btn">
          {loading ? '⏳' : '📤'} Send
        </button>
      </div>
    </div>
  );
};
