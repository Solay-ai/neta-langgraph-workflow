#!/usr/bin/env python3
"""
Simplified Neta workflow without complex LangGraph dependencies
Just the core conversation logic
"""

import json
from datetime import datetime
from typing import Dict, Any, List

def invoke_workflow(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple Neta conversation workflow
    Mimics the LangGraph behavior without dependencies
    """
    
    # Extract input
    business_name = input_data.get("business_name", "")
    messages = input_data.get("messages", [])
    current_step = input_data.get("current_step", "greeting")
    user_data = input_data.get("user_data", {})
    
    print(f"🤖 Neta processing: {business_name} at step {current_step}")
    
    # Conversation logic based on current step
    if current_step == "greeting" or not business_name:
        return greeting_response()
    elif current_step == "social_discovery":
        return social_discovery_response(business_name)
    elif current_step == "content_analysis":
        return content_analysis_response(business_name)
    elif current_step == "content_creation":
        return content_creation_response(business_name)
    else:
        return completion_response(business_name)

def greeting_response():
    """Initial greeting"""
    return {
        "messages": [
            {
                "role": "assistant",
                "content": "Hi! I'm Neta, your AI Marketing Freelancer. I'll help you create amazing social media content based on your existing social presence. What's your business name?",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "current_step": "collect_business_name",
        "user_data": {},
        "social_accounts": [],
        "next_actions": [
            {
                "id": "provide_business_name",
                "label": "Tell me your business name",
                "action": "input_text"
            }
        ]
    }

def social_discovery_response(business_name: str):
    """Social media discovery"""
    discovered_accounts = [
        {
            "platform": "Facebook",
            "name": f"{business_name} Official",
            "followers": "500",
            "verified": True
        },
        {
            "platform": "Instagram", 
            "name": f"@{business_name.lower().replace(' ', '')}",
            "followers": "200",
            "verified": False
        }
    ]
    
    return {
        "messages": [
            {
                "role": "assistant",
                "content": f"Perfect! Let me search for your social media pages...\n\nI found:\n🔵 Facebook: {discovered_accounts[0]['name']} ({discovered_accounts[0]['followers']} followers)\n📸 Instagram: {discovered_accounts[1]['name']} ({discovered_accounts[1]['followers']} followers)\n\nShould I analyze these pages to understand your current content style?",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "current_step": "content_analysis",
        "user_data": {},
        "social_accounts": discovered_accounts,
        "next_actions": [
            {
                "id": "analyze_accounts",
                "label": "Yes, analyze them",
                "action": "confirm"
            }
        ]
    }

def content_analysis_response(business_name: str):
    """Content analysis and strategy"""
    return {
        "messages": [
            {
                "role": "assistant",
                "content": f"Great! I've analyzed your existing posts. I can see you have a casual, friendly tone that your customers love.\n\nBased on your social pages, I'd recommend focusing on:\n✅ Product photography (your shots get 2x more likes!)\n✅ Behind-the-scenes content (trending in your area)\n✅ Customer spotlights (great engagement potential)\n\nShould I create content based on these themes?",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "current_step": "content_creation",
        "user_data": {
            "content_themes": ["product_photography", "behind_the_scenes", "customer_spotlights"],
            "engagement_patterns": {"photos": "2x", "behind_scenes": "trending"}
        },
        "social_accounts": [],
        "next_actions": [
            {
                "id": "create_content",
                "label": "Yes, create content",
                "action": "approve"
            }
        ]
    }

def content_creation_response(business_name: str):
    """Content creation"""
    return {
        "messages": [
            {
                "role": "assistant", 
                "content": f"Perfect! I've created 2 posts based on your successful content patterns:\n\n📱 Post 1: Product showcase (your best-performing type)\n📸 Post 2: Behind-the-scenes content (trending for you)\n\nReady to schedule these posts?",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "current_step": "completion",
        "user_data": {
            "generated_content": [
                {
                    "type": "product_post",
                    "caption": f"Check out what's new at {business_name}! 🌟",
                    "best_time": "2:00 PM"
                }
            ]
        },
        "social_accounts": [],
        "next_actions": [
            {
                "id": "schedule_posts",
                "label": "Schedule posts",
                "action": "schedule"
            }
        ]
    }

def completion_response(business_name: str):
    """Final completion"""
    return {
        "messages": [
            {
                "role": "assistant",
                "content": f"Excellent! Your content is scheduled and ready to go. I'll monitor performance and suggest optimizations. {business_name} is all set for social media success! 🚀",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "current_step": "completed",
        "user_data": {},
        "social_accounts": [],
        "next_actions": []
    }

if __name__ == "__main__":
    # Test the workflow
    test_input = {
        "business_name": "Mike's Pizza",
        "messages": [],
        "current_step": "greeting"
    }
    
    result = invoke_workflow(test_input)
    print(json.dumps(result, indent=2))