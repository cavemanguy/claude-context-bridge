#!/usr/bin/env python3
"""
Universal script for asking Claude questions through the Context Bridge
"""

import asyncio
import json
import websockets
import sys
import uuid

async def ask_claude(message, session_id=None):
    websocket_url = "wss://z33ebwm3q0.execute-api.us-east-1.amazonaws.com/prod"
    
    # Generate session ID if not provided
    if not session_id:
        session_id = f"chat-{uuid.uuid4().hex[:8]}"
    
    print("💬 ASKING CLAUDE")
    print("=" * 30)
    print(f"Session: {session_id}")
    print(f"Question: {message}")
    print()
    print("🔄 Sending...")
    
    try:
        async with websockets.connect(websocket_url) as websocket:
            query = {
                "action": "query",
                "message": message,
                "session_id": session_id
            }
            await websocket.send(json.dumps(query))
            response = await asyncio.wait_for(websocket.recv(), timeout=45)
            
            result = json.loads(response)
            if result.get('statusCode') == 200:
                body = json.loads(result['body'])
                claude_response = body['response']
                context_length = body.get('context_length', 'unknown')
                
                print(f"🤖 Claude: {claude_response}")
                print()
                print(f"📊 Context: {context_length} messages")
                print(f"💾 Session: {session_id}")
                return claude_response, session_id
            else:
                print(f"❌ Error: {result}")
                return None, session_id
                
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None, session_id

def main():
    if len(sys.argv) < 2:
        print("Usage: Ask claude about \"Your question here\" [session_id]")
        sys.exit(1)
    
    message = sys.argv[1]
    session_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    asyncio.run(ask_claude(message, session_id))

if __name__ == "__main__":
    main()