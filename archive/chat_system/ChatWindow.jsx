import React, { useState, useEffect, useRef } from 'react';
import './ChatWindow.css';

/**
 * Three-Way Chat Window
 *
 * Real-time chat interface for Peter, Commentator AI, and Builder AI
 *
 * Features:
 * - Real-time updates via WebSocket
 * - Color-coded messages by sender
 * - Message types (chat, code, review, decision, question, blocker)
 * - File attachment references
 * - Auto-scroll to latest message
 */

const ChatWindow = ({ currentUser = 'peter' }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Fetch initial messages
  useEffect(() => {
    fetchMessages();
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Auto-scroll to latest message
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchMessages = async () => {
    try {
      const response = await fetch('http://localhost:8888/api/chat/messages');
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  const connectWebSocket = () => {
    // Close existing connection if any
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected, skipping');
      return;
    }

    const ws = new WebSocket('ws://localhost:8888/api/chat/stream');

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'initial') {
        setMessages(data.messages || []);
      } else {
        // New message received - avoid duplicates
        setMessages(prev => {
          if (prev.some(m => m.id === data.id)) {
            return prev; // Already exists, don't add
          }
          return [...prev, data];
        });
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('WebSocket closed, reconnecting...');
      setIsConnected(false);
      // Only reconnect if this is still the current connection
      if (wsRef.current === ws) {
        setTimeout(() => connectWebSocket(), 3000);
      }
    };

    wsRef.current = ws;
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const message = {
      sender: currentUser,
      content: input,
      type: 'chat'
    };

    try {
      const response = await fetch('http://localhost:8888/api/chat/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
      });

      if (response.ok) {
        setInput('');
      } else {
        console.error('Failed to send message');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getSenderColor = (sender) => {
    const colors = {
      'peter': '#10b981',      // green
      'commentator': '#3b82f6', // blue
      'builder': '#f97316'      // orange
    };
    return colors[sender] || '#6b7280';
  };

  const getSenderName = (sender) => {
    const names = {
      'peter': 'Peter',
      'commentator': 'Commentator AI',
      'builder': 'Builder AI'
    };
    return names[sender] || sender;
  };

  const getTypeIcon = (type) => {
    const icons = {
      'chat': '💬',
      'code': '💻',
      'review': '📋',
      'decision': '✅',
      'question': '❓',
      'blocker': '🚫'
    };
    return icons[type] || '💬';
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-window">
      {/* Header */}
      <div className="chat-header">
        <h3>Three-Way Chat</h3>
        <div className="connection-status">
          <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`} />
          {isConnected ? 'Connected' : 'Connecting...'}
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="no-messages">
            <p>No messages yet.</p>
            <p>Start the conversation!</p>
          </div>
        )}

        {messages.map(msg => (
          <div
            key={msg.id}
            className={`chat-message ${msg.sender === currentUser ? 'own' : ''}`}
          >
            <div className="message-header">
              <span
                className="sender-name"
                style={{ color: getSenderColor(msg.sender) }}
              >
                {getSenderName(msg.sender)}
              </span>
              <div className="message-meta">
                <span className="message-type">{getTypeIcon(msg.type)}</span>
                <span className="message-time">{formatTime(msg.timestamp)}</span>
              </div>
            </div>

            <div className="message-content">
              {msg.type === 'code' ? (
                <code>{msg.content}</code>
              ) : (
                <span>{msg.content}</span>
              )}
            </div>

            {msg.files && msg.files.length > 0 && (
              <div className="message-files">
                {msg.files.map((file, i) => (
                  <span key={i} className="file-tag">📎 {file}</span>
                ))}
              </div>
            )}
          </div>
        ))}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message... (Shift+Enter for new line)"
          rows={2}
        />
        <button
          onClick={sendMessage}
          disabled={!input.trim() || !isConnected}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;
