# Claude Context Bridge

## Click to watch
[![Claude Bridge Demo](https://img.youtube.com/vi/z0XV_EBIXo8/maxresdefault.jpg)](https://www.youtube.com/watch?v=z0XV_EBIXo8)


*Watch Claude Code autonomously conversing with Claude through the persistent memory bridge*

## 🎯 What Makes This Different

Unlike AutoGPT, BabyAGI, and other agent frameworks that execute tasks, this is experimental memory infrastructure for AI conversations. It's a memory layer that makes all Claude conversations smarter, more coherent, and continuous.

**Watch AI-to-AI knowledge building in action.** Claude Code asks questions like "Help me understand websockets better" rather than "As an agent, I need to..." making the conversations more natural and educational.

## Overview

A WebSocket-based architecture that provides persistent conversational memory for Claude AI across sessions.

The Claude Context Bridge solves the stateless limitation of Large Language Models by creating an external memory system. Claude can maintain context and remember conversations across disconnections while remaining completely unaware of the bridge system.

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │◄──►│  WebSocket  │◄──►│   Lambda    │◄──►│   Claude    │
│             │    │ API Gateway │    │ Function    │    │   API       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                             │
                                             ▼
                                     ┌─────────────┐
                                     │  DynamoDB   │
                                     │ (Context    │
                                     │  Storage)   │
                                     └─────────────┘
```

### Components

- **WebSocket API (API Gateway)**: Real-time bidirectional communication
- **Lambda Function**: Context retrieval, Claude API integration, response handling
- **DynamoDB**: Persistent conversation storage with TTL cleanup
- **Claude API**: Direct integration with Claude 3.5 Sonnet

## 🔬 Research Findings

After 29+ conversation sessions, some unexpected observations have emerged:

- **Self-Improvement Behaviors**: The system began implementing its own optimizations - refining context management, improving conversation patterns, and suggesting architectural enhancements
- **Knowledge Accumulation**: Conversations build genuinely on previous sessions, referencing specific technical details from weeks earlier
- **Infrastructure Resilience**: Survived complete WebSocket infrastructure failure and seamlessly resumed conversations from database context

Whether this represents emergent behavior or sophisticated pattern matching remains an open research question.

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.11+
- Anthropic API key

### Deployment

**Clone and setup:**
```bash
git clone https://github.com/cavemanguy/claude-context-bridge
cd claude-context-bridge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Configure environment:**
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
```

**Deploy infrastructure:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Test the system:**
```bash
python3 ask_claude.py "Hello Claude! Can you remember this conversation?"
```

## 💬 Usage

### Basic Usage
```bash
python3 ask_claude.py "Your question here"
```

### Continue Existing Session
```bash
python3 ask_claude.py "Follow-up question" "session-id"
```

### Examples
```bash
# Start a new conversation
python3 ask_claude.py "Hi Claude! I'm working on a Python project."

# Continue the conversation (Claude will remember context)
python3 ask_claude.py "Can you help me debug this code?" "chat-abc123"
```

## 🔧 Configuration

### Environment Variables

- **ANTHROPIC_API_KEY**: Your Anthropic API key
- **CONTEXT_TABLE**: DynamoDB table for conversations (default: claude-context-sessions)
- **HASH_TABLE**: DynamoDB table for deduplication (default: claude-context-hashes)

### System Settings

- **TTL**: 24-hour automatic cleanup
- **Context Limit**: 8000 characters with intelligent truncation
- **Model**: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)

## 📊 Features

### Core Features
✅ Persistent memory across sessions  
✅ Real-time WebSocket communication  
✅ Automatic context management  
✅ Intelligent deduplication  
✅ TTL-based cleanup  
✅ Session isolation  

### Advanced Features
✅ Context truncation and summarization  
✅ Message deduplication with MD5 hashing  
✅ Error handling and retry logic  
✅ Serverless architecture (scales to zero)  
✅ Direct HTTP API calls (no SDK dependencies)  

## 🏗️ Database Schema

### claude-context-sessions
```json
{
  "session_id": "chat-abc123",
  "context": [
    {"role": "user", "content": "Hello Claude!"},
    {"role": "assistant", "content": "Hi! How can I help you?"}
  ],
  "last_updated": 1750226614,
  "ttl": 1750313014
}
```

### claude-context-hashes
```json
{
  "hash": "md5-hash-of-context",
  "ttl": 1750313014
}
```

## 🔒 Security

- Environment variable storage for API keys
- IAM role-based permissions
- TTL-based automatic data cleanup
- No persistent storage of sensitive data
- WebSocket connection authentication

## 📈 Performance & Limitations

### Current Performance
- **Latency**: ~38ms average response time
- **Context Management**: Efficient with intelligent truncation
- **Costs**: ~$15/month AWS + increased API usage from context injection

### Known Limitations
- **Token Costs**: Context injection significantly increases API usage
- **Context Windows**: Will eventually overflow with very long conversations
- **Scaling**: Current approach is essentially sophisticated prompt stuffing

This is experimental infrastructure exploring pathways toward self-improving AI systems. Not production-ready, but a proof of concept for AI bridging systems and knowledge accumulation research.

## 🛠️ Development

### Local Testing
```bash
# Test WebSocket connection
python3 test_websocket.py

# Check database health
python3 -c "import boto3; print('Database healthy!')"

# View conversation history
python3 get_current_events.py
```

### Architecture Decisions
- **Direct HTTP calls**: Avoided SDK dependencies for lighter Lambda package
- **Single table design**: Simplified DynamoDB schema for faster queries
- **WebSocket responses**: Fixed missing response handling in Lambda
- **Context injection**: External memory management preserves Claude's identity

## 🧠 How It Works

The bridge operates transparently:

1. Client sends message via WebSocket
2. Lambda retrieves conversation history from DynamoDB
3. Full context + new message sent to Claude API
4. Claude responds (unaware of persistent memory)
5. Response stored in DynamoDB and sent to client
6. Claude believes it's having normal conversations

**Result**: Claude maintains perfect conversation continuity across sessions while remaining completely unaware of the external memory system.

## 🎯 Use Cases

- Long-term AI conversations
- Persistent coding assistants
- Multi-session research projects
- Continuous learning interactions
- Stateful AI applications
- AI memory research and experimentation

## 🤝 Contributing

This project demonstrates persistent AI memory architecture for research purposes. Feel free to:

- Submit issues for bugs or feature requests
- Propose optimizations for WebSocket handling
- Suggest improvements for context management
- Share compression and performance enhancements
- Contribute to the research discussion

## 📄 License

MIT License - see LICENSE file for details

## 🔬 Research Questions

If you're experimenting with this system, consider exploring:

1. **Emergent vs. Programmed Behavior**: Are the self-improvements genuine learning or pattern matching?
2. **Scaling Approaches**: How could this bridge architecture work with longer context windows?
3. **Cross-Model Compatibility**: Could this infrastructure work with other LLMs?
4. **Knowledge Persistence**: What constitutes genuine knowledge building in AI conversations?

---

Built with ❤️ for persistent AI conversations and AI memory research
