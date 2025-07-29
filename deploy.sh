#!/bin/bash

# LangGraph Cloud Deployment Script
echo "🚀 Deploying Neta Social Assistant to LangGraph Cloud..."

# Check if langgraph CLI is installed
if ! command -v langgraph &> /dev/null; then
    echo "Installing LangGraph CLI..."
    pip install langgraph-cli
fi

# Set the API key
export LANGCHAIN_API_KEY="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"

# Deploy to LangGraph Cloud
echo "📦 Building and deploying workflow..."
langgraph build

echo "🔄 Deploying to cloud..."
langgraph deploy

echo "✅ Deployment complete!"
echo "📝 Your workflow should now be available at:"
echo "   Assistant ID: neta-social-assistant"
echo "   API endpoint: https://api.smith.langchain.com"

echo ""
echo "🧪 Test your deployment with:"
echo "   curl -X POST https://api.smith.langchain.com/threads/test/runs \\"
echo "     -H 'Authorization: Bearer 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' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"assistant_id\": \"neta-social-assistant\", \"input\": {\"business_name\": \"Test Business\"}}'"