import React from 'react';
import { Navbar } from '@/components/Navbar';
import { ChatHistory } from '@/components/ChatHistory';
import { ChatBox } from '@/components/ChatBox';
import { useChat } from '@/hooks/useChat';
import './App.css';

function App() {
  const { sessions, currentSession, loading, error, createNewSession, setCurrentSession, sendMessage, deleteSession } = useChat();

  const handleNewChat = async () => {
    await createNewSession();
  };

  return (
    <div className="app">
      <Navbar onNewChat={handleNewChat} loading={loading} />
      <div className="app-container">
        <ChatHistory
          sessions={sessions}
          currentSession={currentSession}
          onSelectSession={setCurrentSession}
          onDeleteSession={deleteSession}
          loading={loading}
        />
        <ChatBox session={currentSession} onSendMessage={sendMessage} loading={loading} error={error} />
      </div>
    </div>
  );
}

export default App;
