#!/bin/bash

echo "🚀 Starting FREE Local LangGraph Server..."

# Set environment variables
export LANGSMITH_API_KEY="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"
export OPENAI_API_KEY="your_openai_key_here"

# Install dependencies if needed
if ! python3 -c "import langgraph" &> /dev/null; then
    echo "📦 Installing LangGraph dependencies..."
    pip3 install -r requirements.txt
fi

# Start local PostgreSQL (if using Docker)
if command -v docker &> /dev/null; then
    echo "🐘 Starting PostgreSQL..."
    docker run -d --name langgraph-postgres \
        -e POSTGRES_DB=langgraph \
        -e POSTGRES_USER=langgraph \
        -e POSTGRES_PASSWORD=langgraph \
        -p 5432:5432 \
        postgres:15 || echo "PostgreSQL already running"
    
    echo "📦 Starting Redis..."
    docker run -d --name langgraph-redis \
        -p 6379:6379 \
        redis:7 || echo "Redis already running"
    
    # Wait for services
    sleep 3
    
    export POSTGRES_URI="postgresql://langgraph:langgraph@localhost:5432/langgraph"
    export REDIS_URI="redis://localhost:6379"
fi

# Start LangGraph server
echo "🌟 Starting LangGraph Server on http://localhost:2024"
python3 -m langgraph up --port 2024

# Note: Server will be available at http://localhost:2024
# Your Neta assistant will be at: http://localhost:2024/assistants/neta-social-assistant