#!/bin/bash

set -e

echo "🗄️ Deploying Database Infrastructure..."

# Check for required environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY environment variable not set"
    echo "Run: export ANTHROPIC_API_KEY='your-api-key'"
    exit 1
fi

# Deploy only the database components from main infrastructure
echo "📦 Creating DynamoDB tables..."
aws cloudformation deploy \
    --template-file infrastructure.yaml \
    --stack-name claude-context-bridge \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides AnthropicApiKey="$ANTHROPIC_API_KEY" \
    --region us-east-1

# Check table status
echo "🔍 Verifying table creation..."
aws dynamodb describe-table \
    --table-name claude-context-sessions \
    --region us-east-1 \
    --query 'Table.TableStatus' \
    --output text

aws dynamodb describe-table \
    --table-name claude-context-hashes \
    --region us-east-1 \
    --query 'Table.TableStatus' \
    --output text

echo "✅ Database deployment complete!"
echo "📊 Tables created:"
echo "   - claude-context-sessions (with TTL)"
echo "   - claude-context-hashes (for deduplication)"
echo "🎯 Ready for WebSocket deployment"