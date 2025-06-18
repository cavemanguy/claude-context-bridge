import json
import boto3
import hashlib
import time
import logging
import os
import urllib3
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
CONTEXT_TABLE_NAME = os.environ.get('CONTEXT_TABLE', 'claude-context-sessions')
HASH_TABLE_NAME = os.environ.get('HASH_TABLE', 'claude-context-hashes')

# DynamoDB tables
context_table = dynamodb.Table(CONTEXT_TABLE_NAME)
hash_table = dynamodb.Table(HASH_TABLE_NAME)

# HTTP client
http = urllib3.PoolManager()

class ContextError(Exception):
    pass

class SessionManager:
    @staticmethod
    def generate_session_id(connection_id: str) -> str:
        return hashlib.md5(connection_id.encode()).hexdigest()
    
    @staticmethod
    def get_ttl() -> int:
        return int((datetime.now() + timedelta(hours=24)).timestamp())

class ContextManager:
    def __init__(self):
        self.max_context_length = 8000
        self.max_messages = 50
    
    def store_context(self, session_id: str, context: List[Dict]) -> bool:
        try:
            context_str = json.dumps(context)
            context_hash = hashlib.md5(context_str.encode()).hexdigest()
            
            # Check if we've already stored this exact context
            try:
                hash_response = hash_table.get_item(Key={'hash_id': context_hash})
                if 'Item' in hash_response:
                    logger.info(f"Context already stored with hash {context_hash}")
                    return True
            except Exception as e:
                logger.warning(f"Error checking hash: {e}")
            
            # Store context
            context_table.put_item(
                Item={
                    'session_id': session_id,
                    'context': context,
                    'ttl': SessionManager.get_ttl(),
                    'last_updated': int(time.time())
                }
            )
            
            # Store hash reference
            hash_table.put_item(
                Item={
                    'hash_id': context_hash,
                    'session_id': session_id,
                    'created_at': int(time.time())
                }
            )
            
            logger.info(f"Stored context for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing context: {e}")
            return False
    
    def get_context(self, session_id: str) -> List[Dict]:
        try:
            response = context_table.get_item(Key={'session_id': session_id})
            if 'Item' in response:
                context = response['Item'].get('context', [])
                logger.info(f"Retrieved context for session {session_id}: {len(context)} messages")
                return context
            return []
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def truncate_context(self, context: List[Dict]) -> List[Dict]:
        # Keep system message if present
        system_messages = [msg for msg in context if msg.get('role') == 'system']
        other_messages = [msg for msg in context if msg.get('role') != 'system']
        
        # Truncate by message count
        if len(other_messages) > self.max_messages:
            other_messages = other_messages[-self.max_messages:]
        
        # Truncate by character count
        context_str = json.dumps(other_messages)
        if len(context_str) > self.max_context_length:
            # Remove oldest messages until under limit
            while len(json.dumps(other_messages)) > self.max_context_length and len(other_messages) > 1:
                other_messages.pop(0)
        
        return system_messages + other_messages

class AnthropicService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com"
    
    def create_message(self, messages: List[Dict], system_prompt: Optional[str] = None) -> str:
        try:
            # Prepare the request
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 1000,
                'messages': messages
            }
            
            if system_prompt:
                data['system'] = system_prompt
            
            # Make the request
            response = http.request(
                'POST',
                f'{self.base_url}/v1/messages',
                body=json.dumps(data).encode('utf-8'),
                headers=headers
            )
            
            if response.status == 200:
                result = json.loads(response.data.decode('utf-8'))
                return result['content'][0]['text']
            else:
                logger.error(f"Anthropic API error: {response.status} - {response.data.decode('utf-8')}")
                return "I apologize, but I'm having trouble connecting to my language model right now. Please try again in a moment."
                
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {e}")
            return "I apologize, but I encountered an error while processing your request. Please try again."

class WebSocketHandler:
    def __init__(self):
        self.context_manager = ContextManager()
        self.anthropic_service = AnthropicService(ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
        
    def handle_connect(self, event: Dict[str, Any]) -> Dict[str, Any]:
        connection_id = event['requestContext']['connectionId']
        logger.info(f"WebSocket connected: {connection_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Connected successfully'})
        }
    
    def handle_disconnect(self, event: Dict[str, Any]) -> Dict[str, Any]:
        connection_id = event['requestContext']['connectionId']
        logger.info(f"WebSocket disconnected: {connection_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Disconnected successfully'})
        }
    
    def handle_query(self, event: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Parse the request
            body = json.loads(event.get('body', '{}'))
            message = body.get('message', '')
            connection_id = event['requestContext']['connectionId']
            session_id = body.get('session_id') or SessionManager.generate_session_id(connection_id)
            
            # Get API Gateway endpoint info
            domain_name = event['requestContext']['domainName']
            stage = event['requestContext']['stage']
            
            if not message:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Message is required'})
                }
            
            if not self.anthropic_service:
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Anthropic API not configured'})
                }
            
            # Get existing context
            context = self.context_manager.get_context(session_id)
            
            # Add user message to context
            context.append({'role': 'user', 'content': message})
            
            # Truncate context if needed
            context = self.context_manager.truncate_context(context)
            
            # Prepare messages for API (exclude system messages)
            api_messages = [msg for msg in context if msg.get('role') != 'system']
            
            # Get response from Claude
            system_prompt = "You are Claude, a helpful AI assistant created by Anthropic. You maintain context across our conversation."
            response = self.anthropic_service.create_message(api_messages, system_prompt)
            
            # Add assistant response to context
            context.append({'role': 'assistant', 'content': response})
            
            # Store updated context
            self.context_manager.store_context(session_id, context)
            
            logger.info(f"Successfully processed query for session {session_id}")
            
            # Send response back via WebSocket
            try:
                apigateway = boto3.client('apigatewaymanagementapi', 
                    endpoint_url=f"https://{domain_name}/{stage}")
                
                apigateway.post_to_connection(
                    ConnectionId=connection_id,
                    Data=json.dumps({
                        'statusCode': 200,
                        'body': json.dumps({
                            'response': response,
                            'session_id': session_id,
                            'context_length': len(context)
                        })
                    })
                )
                
                logger.info(f"Response sent to WebSocket connection {connection_id}")
                
            except Exception as e:
                logger.error(f"Error sending WebSocket response: {e}")
                # Still return success since the processing worked
            
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Query processed successfully'})
            }
            
        except Exception as e:
            logger.error(f"Error handling query: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Internal server error'})
            }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for WebSocket events
    """
    try:
        route_key = event['requestContext']['routeKey']
        handler = WebSocketHandler()
        
        logger.info(f"Handling route: {route_key}")
        
        if route_key == '$connect':
            return handler.handle_connect(event)
        elif route_key == '$disconnect':
            return handler.handle_disconnect(event)
        elif route_key == 'query':
            return handler.handle_query(event)
        else:
            logger.warning(f"Unknown route: {route_key}")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unknown route: {route_key}'})
            }
            
    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }