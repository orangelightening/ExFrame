#!/usr/bin/env python3
"""
Read messages from the three-way chat.

Usage:
    # Read all messages
    python3 chat_read.py

    # Read only messages from peter
    python3 chat_read.py --sender peter

    # Read last 5 messages
    python3 chat_read.py --limit 5

    # Read messages since a timestamp
    python3 chat_read.py --since "2026-01-05T02:00:00"

    # Watch mode - poll for new messages every 2 seconds
    python3 chat_read.py --watch
"""

import sys
import json
import urllib.request
import urllib.error
import time
from datetime import datetime
from typing import List, Dict

def get_messages(since: str = None) -> List[Dict]:
    """Get messages from the chat API"""
    url = "http://localhost:8888/api/chat/messages"
    if since:
        url += f"?since={since}"

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("messages", [])
    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code}: {e.reason}", file=sys.stderr)
        return []
    except urllib.error.URLError as e:
        print(f"[ERROR] Cannot connect to chat server: {e.reason}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return []

def format_message(msg: Dict) -> str:
    """Format a message for display"""
    sender = msg.get("sender", "unknown")
    content = msg.get("content", "")
    msg_type = msg.get("type", "chat")
    timestamp = msg.get("timestamp", "")

    # Format time
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

def filter_by_sender(messages: List[Dict], sender: str) -> List[Dict]:
    """Filter messages by sender"""
    return [m for m in messages if m.get("sender") == sender]

def print_messages(messages: List[Dict], limit: int = None):
    """Print messages to stdout"""
    if limit:
        messages = messages[-limit:]

    if not messages:
        print("[INFO] No messages found")
        return

    for msg in messages:
        print(format_message(msg))

def watch_messages(since: str = None, interval: int = 2):
    """Watch for new messages in a loop"""
    print("[INFO] Watching for new messages... (Ctrl+C to exit)")
    last_timestamp = since

    try:
        while True:
            messages = get_messages(since=last_timestamp)
            if messages:
                print("\n[NEW MESSAGES]")
                print_messages(messages)
                last_timestamp = messages[-1].get("timestamp")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[INFO] Stopped watching")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Read messages from the three-way chat")
    parser.add_argument("--sender", help="Filter by sender (peter, commentator, builder)")
    parser.add_argument("--limit", type=int, help="Limit number of messages")
    parser.add_argument("--since", help="Only messages after this timestamp (ISO format)")
    parser.add_argument("--watch", action="store_true", help="Watch mode - poll for new messages")
    parser.add_argument("--interval", type=int, default=2, help="Watch interval in seconds (default: 2)")

    args = parser.parse_args()

    if args.watch:
        watch_messages(args.since, args.interval)
    else:
        messages = get_messages(args.since)

        if args.sender:
            messages = filter_by_sender(messages, args.sender)

        print_messages(messages, args.limit)
