"""
Three-Way Chat System - Backend API

FastAPI server for real-time chat between:
- Peter (Human director)
- Commentator GLM-4.7 (Architecture/Review)
- Builder GLM-4.7 (Implementation)

Features:
- WebSocket real-time updates
- Message persistence
- CLI access for AIs
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import uuid
import asyncio
from pathlib import Path

app = FastAPI(title="Three-Way Chat API")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage
MESSAGES_FILE = Path("data/chat/messages.json")
MESSAGES_FILE.parent.mkdir(parents=True, exist_ok=True)

# WebSocket connections
connections: List[WebSocket] = []

# Data models
class Message(BaseModel):
    sender: str  # "peter", "commentator", "builder"
    content: str
    type: str = "chat"
    mentions: List[str] = []
    files: List[str] = []

class MessageResponse(BaseModel):
    id: str
    timestamp: str
    sender: str
    content: str
    type: str
    mentions: List[str]
    files: List[str]

# Helper functions
def load_messages() -> dict:
    """Load all messages from storage"""
    if not MESSAGES_FILE.exists():
        return {"messages": [], "last_updated": datetime.utcnow().isoformat()}

    with open(MESSAGES_FILE, 'r') as f:
        return json.load(f)

def save_messages(data: dict):
    """Save messages to storage"""
    data["last_updated"] = datetime.utcnow().isoformat()
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def broadcast_message(message: dict):
    """Send message to all connected clients"""
    disconnected = []
    for connection in connections:
        try:
            asyncio.create_task(connection.send_json(message))
        except:
            disconnected.append(connection)

    for conn in disconnected:
        connections.remove(conn)

# Endpoints
@app.post("/api/chat/messages", response_model=MessageResponse)
async def send_message(message: Message):
    """Send a new message"""
    if message.sender not in ["peter", "commentator", "builder"]:
        raise HTTPException(status_code=400, detail="Invalid sender")

    data = load_messages()

    new_message = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "sender": message.sender,
        "content": message.content,
        "type": message.type,
        "mentions": message.mentions,
        "files": message.files,
        "metadata": {}
    }

    data["messages"].append(new_message)
    save_messages(data)

    # Broadcast to all connected clients
    broadcast_message(new_message)

    return new_message

@app.get("/api/chat/messages")
async def get_messages(since: Optional[str] = None):
    """Get all messages or messages since timestamp"""
    data = load_messages()
    messages = data["messages"]

    if since:
        messages = [m for m in messages if m["timestamp"] > since]

    return {
        "messages": messages,
        "count": len(messages)
    }

@app.websocket("/api/chat/stream")
async def chat_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    connections.append(websocket)

    try:
        # Send initial messages
        data = load_messages()
        await websocket.send_json({"type": "initial", "messages": data["messages"]})

        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.remove(websocket)
    except Exception as e:
        connections.remove(websocket)

@app.get("/api/chat/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "connections": len(connections),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Three-Way Chat API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/chat/messages": "Send a message",
            "GET /api/chat/messages": "Get all messages",
            "WS /api/chat/stream": "WebSocket for real-time updates",
            "GET /api/chat/health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
