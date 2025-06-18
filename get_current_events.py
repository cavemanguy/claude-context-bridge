#!/usr/bin/env python3
"""
Retrieve the current events conversation from the database
"""

import boto3
import json
from decimal import Decimal

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def get_conversation():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('claude-context-sessions')
    
    # Look for current events sessions
    response = table.scan()
    
    current_events_sessions = []
    for item in response['Items']:
        if 'current-events' in item['session_id']:
            current_events_sessions.append(item)
    
    if current_events_sessions:
        # Get the most recent session
        latest_session = max(current_events_sessions, key=lambda x: x.get('updated_at', ''))
        
        print("📰 CURRENT EVENTS CONVERSATION")
        print("=" * 50)
        print(f"Session ID: {latest_session['session_id']}")
        print(f"Total Messages: {len(latest_session.get('messages', []))}")
        print(f"Last Updated: {latest_session.get('updated_at', 'unknown')}")
        print()
        
        messages = latest_session.get('messages', [])
        for i, msg in enumerate(messages, 1):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            
            if role == 'user':
                print(f"💬 Steve: {content}")
            elif role == 'assistant':
                print(f"🤖 Claude: {content}")
            
            print()
            if i < len(messages) and i % 2 == 0:  # Add separator after each Q&A pair
                print("-" * 30)
                print()
        
        print("✅ Current events conversation retrieved!")
        return latest_session
    else:
        print("❌ No current events sessions found")
        return None

if __name__ == "__main__":
    get_conversation()