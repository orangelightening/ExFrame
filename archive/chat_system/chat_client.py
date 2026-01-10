#!/usr/bin/env python3
"""
Interactive chat client for AI agents.

This script watches the chat for new messages and can be used to send responses.
Designed for use with AI tools that can execute Python scripts.

Usage as Commentator AI:
    python3 chat_client.py commentator

Usage as Builder AI:
    python3 chat_client.py builder

The client will:
1. Show existing messages
2. Watch for new messages
3. Allow sending responses via the send_message() function

Example for AI agents:
    "Read the latest messages using chat_read.py, then respond using chat_send.py"
"""

import sys
import os
import time
import json
import urllib.request
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ChatClient:
    """Simple chat client for AI agents"""

    def __init__(self, agent_name: str):
        if agent_name not in ["commentator", "builder"]:
            print(f"Error: agent_name must be 'commentator' or 'builder', got '{agent_name}'")
            sys.exit(1)
        self.agent_name = agent_name
        self.base_url = "http://localhost:8888"
        self.last_timestamp = None

    def get_messages(self, since: str = None) -> list:
        """Get messages from the chat"""
        url = f"{self.base_url}/api/chat/messages"
        if since:
            url += f"?since={since}"

        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("messages", [])
        except Exception as e:
            print(f"[ERROR] Failed to get messages: {e}")
            return []

    def send_message(self, content: str, msg_type: str = "chat") -> bool:
        """Send a message to the chat"""
        url = f"{self.base_url}/api/chat/messages"
        message = {
            "sender": self.agent_name,
            "content": content,
            "type": msg_type,
            "mentions": [],
            "files": []
        }

        try:
            data = json.dumps(message).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            req.get_method = lambda: "POST"

            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode("utf-8"))
                print(f"[SENT] {self.agent_name}: {content[:50]}...")
                return True
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
            return False

    def format_message(self, msg: dict) -> str:
        """Format a message for display"""
        sender = msg.get("sender", "unknown")
        content = msg.get("content", "")
        msg_type = msg.get("type", "chat")
        timestamp = msg.get("timestamp", "")

        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            time_str = dt.strftime("%H:%M:%S")
        except:
            time_str = timestamp[:19] if timestamp else "??"

        type_icons = {
            "chat": "💬",
            "code": "💻",
            "review": "📋",
            "decision": "✅",
            "question": "❓",
            "blocker": "🚫"
        }
        icon = type_icons.get(msg_type, "💬")

        return f"[{time_str}] {icon} {sender}: {content}"

    def show_messages(self, messages: list):
        """Display messages"""
        if not messages:
            print("[INFO] No messages")
            return

        print(f"\n{'='*60}")
        for msg in messages:
            print(self.format_message(msg))
        print(f"{'='*60}\n")

    def watch_once(self) -> list:
        """Get new messages since last check"""
        messages = self.get_messages(since=self.last_timestamp)
        if messages:
            self.last_timestamp = messages[-1].get("timestamp")
        return messages

    def watch_loop(self, interval: int = 2):
        """Continuously watch for new messages"""
        print(f"\n{'='*60}")
        print(f" Chat Client for {self.agent_name.upper()}")
        print(f"{'='*60}")
        print(f"[INFO] Watching for messages (Ctrl+C to exit)")

        # Show recent messages first
        initial = self.get_messages()
        if initial:
            print(f"\n[RECENT] Last {min(5, len(initial))} messages:")
            self.show_messages(initial[-5:])
            if initial:
                self.last_timestamp = initial[-1].get("timestamp")

        try:
            while True:
                new_messages = self.watch_once()
                if new_messages:
                    print(f"\n[NEW MESSAGES] ({len(new_messages)})")
                    self.show_messages(new_messages)
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n[INFO] {self.agent_name} client stopped")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python3 chat_client.py <commentator|builder>")
        sys.exit(1)

    agent_name = sys.argv[1]
    client = ChatClient(agent_name)

    # Check for commands
    if len(sys.argv) > 2:
        command = sys.argv[2]

        if command == "send":
            if len(sys.argv) < 4:
                print("Usage: python3 chat_client.py <agent> send <message> [type]")
                sys.exit(1)
            content = sys.argv[3]
            msg_type = sys.argv[4] if len(sys.argv) > 4 else "chat"
            success = client.send_message(content, msg_type)
            sys.exit(0 if success else 1)

        elif command == "read":
            messages = client.get_messages()
            client.show_messages(messages)

        elif command == "watch":
            interval = int(sys.argv[3]) if len(sys.argv) > 3 else 2
            client.watch_loop(interval)

        else:
            print(f"Unknown command: {command}")
            print("Available commands: send, read, watch")
            sys.exit(1)
    else:
        # Default: start watch loop
        client.watch_loop()


if __name__ == "__main__":
    main()
