#!/bin/bash

set -e

echo "🚀 Deploying Claude Context Bridge..."

# Check for required environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY environment variable not set"
    echo "Run: export ANTHROPIC_API_KEY='your-api-key'"
    exit 1
fi

# Deploy CloudFormation stack
echo "📦 Deploying infrastructure..."
aws cloudformation deploy \
    --template-file infrastructure.yaml \
    --stack-name claude-context-bridge \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides AnthropicApiKey="$ANTHROPIC_API_KEY" \
    --region us-east-1

# Package and deploy Lambda function
echo "🔧 Packaging Lambda function..."
zip -r lambda-deployment.zip lambda_function.py

# Update Lambda function code
echo "📤 Updating Lambda function..."
aws lambda update-function-code \
    --function-name claude-context-bridge \
    --zip-file fileb://lambda-deployment.zip \
    --region us-east-1

# Get WebSocket URL
WEBSOCKET_URL=$(aws cloudformation describe-stacks \
    --stack-name claude-context-bridge \
    --query 'Stacks[0].Outputs[?OutputKey==`WebSocketURL`].OutputValue' \
    --output text \
    --region us-east-1)

echo "✅ Deployment complete!"
echo "🔗 WebSocket URL: $WEBSOCKET_URL"
echo "💾 Save this URL for your terminal agent configuration"

# Cleanup
rm -f lambda-deployment.zip

echo "🎉 Ready to test!"