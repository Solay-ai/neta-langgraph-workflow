# Neta Social Assistant - LangGraph Workflow

## Overview
AI Marketing Freelancer for social media automation and guidance. This workflow provides a complete conversational experience for small business owners to discover their social presence, analyze content, and get content strategy.

## Workflow Steps
1. **Greeting** - Initial welcome and business name collection
2. **Social Discovery** - Find and analyze existing social media accounts  
3. **Content Analysis** - Analyze existing content and create strategy recommendations
4. **Content Creation** - Generate actual posts based on strategy
5. **Completion** - Final confirmation and scheduling

## Configuration
- **Graph ID**: `neta-social-assistant`
- **Entry Point**: `neta_social_assistant.py:app`
- **Model**: GPT-4o-mini with 0.7 temperature
- **Max Tokens**: 1000

## Environment Variables Required
- `OPENAI_API_KEY`: Your OpenAI API key for content generation
- `LANGCHAIN_API_KEY`: Your LangSmith API key for tracing
- `LANGSMITH_API_KEY`: Same as LANGCHAIN_API_KEY

## Input Schema
```json
{
  "business_name": "string",
  "messages": "array",
  "current_step": "string", 
  "user_data": "object"
}
```

## Output Schema  
```json
{
  "messages": "array",
  "current_step": "string",
  "user_data": "object",
  "social_accounts": "array",
  "next_actions": "array"
}
```

## Testing
Test the workflow locally:
```bash
python neta_social_assistant.py
```

## Deployment
This workflow is configured for LangGraph Cloud deployment with the Plus plan.