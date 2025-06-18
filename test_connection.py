#!/usr/bin/env python3
"""
Test the Claude Context Bridge WebSocket connection
"""

import asyncio
import json
import websockets

async def test_bridge():
    # Update this URL after deployment
    websocket_url = "wss://your-api-id.execute-api.us-east-1.amazonaws.com/prod"
    
    print("🔗 Testing Claude Context Bridge...")
    
    try:
        async with websockets.connect(websocket_url) as websocket:
            print("✅ Connected to WebSocket!")
            
            query = {
                "action": "query",
                "message": "Hello Claude! This is a test of the bridge system.",
                "session_id": "test-session"
            }
            
            print("📤 Sending test message...")
            await websocket.send(json.dumps(query))
            
            print("📥 Waiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=30)
            
            result = json.loads(response)
            if result.get('statusCode') == 200:
                body = json.loads(result['body'])
                print(f"🤖 Claude: {body['response']}")
                print("✅ Bridge system working!")
            else:
                print(f"❌ Error: {result}")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_bridge())