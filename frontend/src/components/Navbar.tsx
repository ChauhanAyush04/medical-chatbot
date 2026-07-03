import React from 'react';
import '../styles/navbar.css';

interface NavbarProps {
  onNewChat: () => void;
  loading: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onNewChat, loading }) => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <h1>💊 Medical ChatBot</h1>
          <p>Professional Medical Information Assistant</p>
        </div>
        <button className="new-chat-btn" onClick={onNewChat} disabled={loading}>
          ➕ New Chat
        </button>
      </div>
    </nav>
  );
};
