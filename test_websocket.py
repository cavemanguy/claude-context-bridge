#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_connection():
    websocket_url = "wss://z33ebwm3q0.execute-api.us-east-1.amazonaws.com/prod"
    
    try:
        print("🔗 Testing WebSocket connection...")
        async with websockets.connect(websocket_url) as websocket:
            print("✅ Connected successfully!")
            
            # Send a simple test message
            test_query = {
                "action": "query",
                "message": "Hello Claude, just testing the connection!",
                "session_id": "test-connection"
            }
            
            print("📤 Sending test message...")
            await websocket.send(json.dumps(test_query))
            
            print("📥 Waiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=30)
            
            print("🎉 Received response!")
            result = json.loads(response)
            print(f"Status: {result.get('statusCode')}")
            
            if result.get('statusCode') == 200:
                body = json.loads(result['body'])
                print(f"Claude: {body.get('response', 'No response')}")
            else:
                print(f"Error: {result}")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_connection())