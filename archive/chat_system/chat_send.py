#!/usr/bin/env python3
"""
Send a message to the three-way chat.

Usage:
    python3 chat_send.py "commentator" "This is my message" "chat"
    python3 chat_send.py "builder" "Here's some code" "code"

Arguments:
    sender: "peter", "commentator", or "builder"
    content: The message text
    type: "chat", "code", "review", "decision", "question", or "blocker" (default: "chat")
"""

import sys
import json
import urllib.request
import urllib.error

def send_message(sender: str, content: str, msg_type: str = "chat"):
    """Send a message to the chat API"""
    url = "http://localhost:8888/api/chat/messages"

    message = {
        "sender": sender,
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
            print(f"[OK] Message sent as {sender} (ID: {result['id']})")
            return True
    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"[ERROR] Cannot connect to chat server: {e.reason}")
        print(f"[INFO] Make sure the chat server is running on port 8888")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nError: At least 2 arguments required (sender, content)")
        sys.exit(1)

    sender = sys.argv[1]
    content = sys.argv[2]
    msg_type = sys.argv[3] if len(sys.argv) > 3 else "chat"

    # Validate sender
    if sender not in ["peter", "commentator", "builder"]:
        print(f"[ERROR] Invalid sender: {sender}")
        print("[INFO] Valid senders: peter, commentator, builder")
        sys.exit(1)

    # Validate message type
    valid_types = ["chat", "code", "review", "decision", "question", "blocker"]
    if msg_type not in valid_types:
        print(f"[ERROR] Invalid message type: {msg_type}")
        print(f"[INFO] Valid types: {', '.join(valid_types)}")
        sys.exit(1)

    success = send_message(sender, content, msg_type)
    sys.exit(0 if success else 1)
