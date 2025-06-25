# Claude Context Bridge

## Overview
A WebSocket-based architecture that provides persistent conversational memory for Claude AI across sessions through intelligent context injection.

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

## 🧠 How It Actually Works

**The Reality:**
This system provides sophisticated **memory injection**, not autonomous AI-to-AI communication. Here's what actually happens:

1. **Client sends message** via WebSocket
2. **Lambda retrieves** conversation history from DynamoDB
3. **Context injection**: Previous conversations are included in Claude's prompt as conversation history
4. **Claude responds** based on the full context (unaware of the memory system)
5. **Response stored** in DynamoDB and sent to client

**What Claude Experiences:**
Claude sees what appears to be a continuous conversation thread, but it's actually receiving carefully managed context from previous sessions. It responds naturally to this injected context, creating the appearance of persistent memory.

**What This Enables:**
- Conversations that build on previous sessions
- Complex project continuity over time
- Knowledge accumulation through context management
- Coherent long-term interactions

## 🔬 Research Findings

After 29+ conversation sessions, interesting patterns have emerged:

**Observed Behaviors:**
- **Context Building**: Conversations genuinely reference specific details from previous sessions
- **Project Continuity**: Complex projects develop across multiple sessions
- **Pattern Consistency**: Responses maintain coherence with injected historical context
- **Infrastructure Interactions**: Claude can work with and modify AWS resources based on previous context

**Important Note**: These behaviors result from sophisticated context management rather than autonomous AI decision-making. Claude responds to the provided context naturally, but isn't consciously "remembering" or making autonomous decisions to build on previous work.

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Python 3.11+
- Anthropic API key

### Deployment
Clone and setup:
```bash
git clone https://github.com/cavemanguy/claude-context-bridge
cd claude-context-bridge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure environment:
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
```

Deploy infrastructure:
```bash
chmod +x deploy.sh
./deploy.sh
```

Test the system:
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

# Continue the conversation (Claude will have context from previous session)
python3 ask_claude.py "Can you help me debug this code?" "chat-abc123"
```

## 🔧 Configuration

### Environment Variables
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `CONTEXT_TABLE`: DynamoDB table for conversations (default: claude-context-sessions)
- `HASH_TABLE`: DynamoDB table for deduplication (default: claude-context-hashes)

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
- **Scaling**: Current approach is sophisticated prompt engineering, not true AI memory
- **Dependency**: Requires careful context management to maintain coherence

## 🎯 Use Cases
- Long-term AI conversations
- Persistent coding assistants
- Multi-session research projects
- Continuous learning interactions
- Stateful AI applications
- AI memory research and experimentation

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

## 🔬 Research Questions

This system demonstrates sophisticated context management for AI conversations. Consider exploring:

1. **Context vs. Memory**: What's the difference between injected context and genuine AI memory?
2. **Scaling Approaches**: How could this architecture work with longer context windows?
3. **Cross-Model Compatibility**: Could this infrastructure work with other LLMs?
4. **Behavioral Emergence**: Do consistent patterns in context injection create emergent-like behaviors?
5. **Memory Architecture**: What would true persistent AI memory look like vs. context management?

## 🤝 Contributing

This project demonstrates persistent AI context architecture for research purposes. Feel free to:

- Submit issues for bugs or feature requests
- Propose optimizations for WebSocket handling
- Suggest improvements for context management
- Share compression and performance enhancements
- Contribute to the research discussion

## 📄 License
MIT License - see LICENSE file for details

---

**Note**: This is experimental infrastructure exploring sophisticated context management for AI systems. It demonstrates how external memory systems can enhance AI conversations through intelligent context injection, creating the appearance of persistent memory and continuity across sessions.
