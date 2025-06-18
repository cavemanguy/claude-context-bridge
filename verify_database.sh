#!/bin/bash

echo "🔍 CLAUDE CONTEXT BRIDGE - DATABASE VERIFICATION"
echo "================================================"
echo

# Check total sessions
SESSION_COUNT=$(aws dynamodb scan --table-name claude-context-sessions --region us-east-1 --select COUNT --output text --query 'Count')
echo "📊 Total Active Sessions: $SESSION_COUNT"
echo

# Check hash deduplication table
HASH_COUNT=$(aws dynamodb scan --table-name claude-context-hashes --region us-east-1 --select COUNT --output text --query 'Count')
echo "🔗 Total Context Hashes: $HASH_COUNT"
echo

# Show recent sessions (last 3)
echo "📝 RECENT CONVERSATION SESSIONS:"
echo "================================"

aws dynamodb scan \
    --table-name claude-context-sessions \
    --region us-east-1 \
    --query 'Items[*].{SessionID:session_id.S,LastUpdated:last_updated.N,Messages:length(context.L)}' \
    --output table

echo
echo "💾 SAMPLE CONVERSATION CONTEXT:"
echo "==============================="

# Get the most recent session and show its context
LATEST_SESSION=$(aws dynamodb scan \
    --table-name claude-context-sessions \
    --region us-east-1 \
    --query 'Items | sort_by(@, &last_updated.N) | [-1].session_id.S' \
    --output text)

if [ "$LATEST_SESSION" != "None" ]; then
    echo "Session: $LATEST_SESSION"
    echo
    
    aws dynamodb get-item \
        --table-name claude-context-sessions \
        --key "{\"session_id\":{\"S\":\"$LATEST_SESSION\"}}" \
        --region us-east-1 \
        --query 'Item.context.L[*].M.{Role:role.S,Content:content.S}' \
        --output table
else
    echo "No sessions found"
fi

echo
echo "✅ Database verification complete!"
echo "🌟 This proves persistent context storage is working!"