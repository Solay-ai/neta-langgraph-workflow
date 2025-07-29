"""
Neta Social Assistant - LangGraph Cloud Workflow
AI Marketing Freelancer for social media automation and guidance
"""

from typing import Dict, Any, List, Optional, Literal
from typing_extensions import TypedDict
from langgraph import Graph, StateGraph
from langgraph.graph import END, START
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
import json
import uuid

# State Schema
class NetaState(TypedDict):
    business_name: str
    messages: List[Dict[str, Any]]
    current_step: str
    user_data: Dict[str, Any]
    social_accounts: List[Dict[str, Any]]
    next_actions: List[Dict[str, Any]]
    session_id: str

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000
)

def greeting_node(state: NetaState) -> NetaState:
    """Initial greeting and business name collection"""
    
    if not state.get("business_name"):
        greeting_msg = {
            "role": "assistant",
            "content": "Hi! I'm Neta, your AI Marketing Freelancer. I'll help you create amazing social media content based on your existing social presence. What's your business name?",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return {
            **state,
            "messages": state.get("messages", []) + [greeting_msg],
            "current_step": "collect_business_name",
            "next_actions": [
                {
                    "id": "provide_business_name",
                    "label": "Tell me your business name",
                    "action": "input_text"
                }
            ]
        }
    
    return {
        **state,
        "current_step": "social_discovery"
    }

def social_discovery_node(state: NetaState) -> NetaState:
    """Search and analyze existing social media accounts"""
    
    business_name = state.get("business_name", "")
    
    # Simulate social media discovery (in real implementation, this would call APIs)
    discovered_accounts = [
        {
            "platform": "Facebook",
            "name": f"{business_name} Official",
            "url": f"https://facebook.com/{business_name.lower().replace(' ', '')}",
            "followers": "500",
            "verified": True
        },
        {
            "platform": "Instagram", 
            "name": f"@{business_name.lower().replace(' ', '')}",
            "url": f"https://instagram.com/{business_name.lower().replace(' ', '')}",
            "followers": "200",
            "verified": False
        }
    ]
    
    discovery_msg = {
        "role": "assistant",
        "content": f"Perfect! Let me search for your social media pages...\n\nI found:\n🔵 Facebook: {discovered_accounts[0]['name']} ({discovered_accounts[0]['followers']} followers)\n📸 Instagram: {discovered_accounts[1]['name']} ({discovered_accounts[1]['followers']} followers)\n\nShould I analyze these pages to understand your current content style?",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    return {
        **state,
        "messages": state.get("messages", []) + [discovery_msg],
        "current_step": "confirm_accounts",
        "social_accounts": discovered_accounts,
        "next_actions": [
            {
                "id": "analyze_accounts",
                "label": "Yes, analyze them",
                "action": "confirm"
            },
            {
                "id": "add_more_accounts",
                "label": "Let me add more accounts",
                "action": "modify"
            },
            {
                "id": "no_social_pages",
                "label": "I don't have social pages yet",
                "action": "create_new"
            }
        ]
    }

def content_analysis_node(state: NetaState) -> NetaState:
    """Analyze existing content and create strategy"""
    
    business_name = state.get("business_name", "")
    
    analysis_msg = {
        "role": "assistant", 
        "content": f"Great! I've analyzed your existing posts. I can see you have a casual, friendly tone that your customers love.\n\nBased on your social pages, I'd recommend focusing on:\n✅ Food photography (your pizza shots get 2x more likes!)\n✅ Behind-the-scenes kitchen content (trending in your area)\n✅ Customer spotlights (great engagement potential)\n\nShould I create a content strategy around these themes?",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    return {
        **state,
        "messages": state.get("messages", []) + [analysis_msg],
        "current_step": "strategy_approval",
        "user_data": {
            **state.get("user_data", {}),
            "content_themes": ["food_photography", "behind_the_scenes", "customer_spotlights"],
            "best_performing_content": "pizza_photos",
            "engagement_patterns": {"photos": "2x", "behind_scenes": "trending"}
        },
        "next_actions": [
            {
                "id": "approve_strategy",
                "label": "Sounds perfect",
                "action": "approve"
            },
            {
                "id": "adjust_themes",
                "label": "Let me adjust these themes",
                "action": "modify"
            },
            {
                "id": "show_examples",
                "label": "Show me examples first",
                "action": "preview"
            }
        ]
    }

def content_creation_node(state: NetaState) -> NetaState:
    """Generate content based on strategy"""
    
    business_name = state.get("business_name", "")
    
    creation_msg = {
        "role": "assistant",
        "content": f"Perfect! I'll create content that matches your existing style. Let me show you what I'm doing:\n\n🔍 Analyzing your best-performing posts from last month...\n📊 Researching trending hashtags in your area...\n🎨 Creating images that match your visual style...\n✍️ Writing captions in your friendly tone...\n\nThis will take about 2 minutes. I'll show you everything before posting anything.",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    # Simulate content generation
    generated_content = [
        {
            "id": "post_1",
            "type": "image_post",
            "caption": f"Fresh pizza straight from {business_name}'s oven! 🍕 What's your favorite topping combination? #FreshPizza #LocalEats #PizzaLovers",
            "image_description": "Steaming hot pizza with melted cheese",
            "hashtags": ["#FreshPizza", "#LocalEats", "#PizzaLovers"],
            "best_time": "2:00 PM"
        },
        {
            "id": "post_2", 
            "type": "behind_scenes",
            "caption": f"Behind the scenes at {business_name} - our chef putting love into every pizza! 👨‍🍳 #BehindTheScenes #HandCrafted #Pizza",
            "image_description": "Chef preparing pizza dough",
            "hashtags": ["#BehindTheScenes", "#HandCrafted", "#Pizza"],
            "best_time": "10:00 AM"
        }
    ]
    
    content_msg = {
        "role": "assistant",
        "content": f"Here are 2 posts I've created based on your social presence. Each one follows the style of your most successful content:\n\n📱 Post 1: Pizza photo (your best-performing type)\n📸 Post 2: Behind-the-scenes content (trending for you)\n\nWould you like to review and approve these posts?",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    return {
        **state,
        "messages": state.get("messages", []) + [creation_msg, content_msg],
        "current_step": "content_approval",
        "user_data": {
            **state.get("user_data", {}),
            "generated_content": generated_content
        },
        "next_actions": [
            {
                "id": "approve_all",
                "label": "Post all now",
                "action": "approve_all"
            },
            {
                "id": "review_individual",
                "label": "Let me review each one",
                "action": "review"
            },
            {
                "id": "create_different",
                "label": "Create different styles",
                "action": "regenerate"
            }
        ]
    }

def completion_node(state: NetaState) -> NetaState:
    """Final confirmation and scheduling"""
    
    completion_msg = {
        "role": "assistant",
        "content": "Perfect! Your content is ready to go:\n\n📱 Post 1: Going to Facebook at 2:00 PM (your best engagement time)\n📸 Post 2: Going to Instagram at 2:05 PM\n\nI'll monitor the performance and suggest optimizations based on engagement. You're all set!",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    return {
        **state,
        "messages": state.get("messages", []) + [completion_msg],
        "current_step": "completed",
        "next_actions": []
    }

def route_next_step(state: NetaState) -> Literal["greeting", "social_discovery", "content_analysis", "content_creation", "completion", END]:
    """Router function to determine next step"""
    
    current_step = state.get("current_step", "greeting")
    
    if current_step == "greeting" or current_step == "collect_business_name":
        if state.get("business_name"):
            return "social_discovery"
        return "greeting"
    elif current_step == "social_discovery" or current_step == "confirm_accounts":
        return "content_analysis"
    elif current_step == "strategy_approval":
        return "content_creation" 
    elif current_step == "content_approval":
        return "completion"
    elif current_step == "completed":
        return END
    else:
        return "greeting"

# Build the workflow graph
workflow = StateGraph(NetaState)

# Add nodes
workflow.add_node("greeting", greeting_node)
workflow.add_node("social_discovery", social_discovery_node)
workflow.add_node("content_analysis", content_analysis_node)
workflow.add_node("content_creation", content_creation_node)
workflow.add_node("completion", completion_node)

# Add edges
workflow.add_edge(START, "greeting")
workflow.add_conditional_edges(
    "greeting",
    route_next_step,
    {
        "greeting": "greeting",
        "social_discovery": "social_discovery"
    }
)
workflow.add_conditional_edges(
    "social_discovery", 
    route_next_step,
    {
        "content_analysis": "content_analysis"
    }
)
workflow.add_conditional_edges(
    "content_analysis",
    route_next_step,
    {
        "content_creation": "content_creation"
    }
)
workflow.add_conditional_edges(
    "content_creation",
    route_next_step,
    {
        "completion": "completion"
    }
)
workflow.add_conditional_edges(
    "completion",
    route_next_step,
    {
        END: END
    }
)

# Compile the graph
app = workflow.compile()

# Entry point for LangGraph Cloud
def invoke_workflow(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for the workflow"""
    
    # Extract input
    business_name = input_data.get("business_name", "")
    messages = input_data.get("messages", [])
    current_step = input_data.get("current_step", "greeting")
    user_data = input_data.get("user_data", {})
    
    # Initialize state
    initial_state = NetaState(
        business_name=business_name,
        messages=messages,
        current_step=current_step,
        user_data=user_data,
        social_accounts=[],
        next_actions=[],
        session_id=str(uuid.uuid4())
    )
    
    # Run the workflow
    result = app.invoke(initial_state)
    
    return {
        "messages": result["messages"],
        "current_step": result["current_step"],
        "user_data": result["user_data"],
        "social_accounts": result.get("social_accounts", []),
        "next_actions": result.get("next_actions", [])
    }

if __name__ == "__main__":
    # Test the workflow locally
    test_input = {
        "business_name": "Mike's Pizza",
        "messages": [
            {
                "role": "user",
                "content": "Mike's Pizza",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        ],
        "current_step": "greeting",
        "user_data": {}
    }
    
    result = invoke_workflow(test_input)
    print(json.dumps(result, indent=2))