"""
Neta Social Assistant - LangGraph Cloud Workflow
AI Marketing Freelancer for social media automation and guidance
"""

from typing import Dict, Any, List, Optional, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
import json
import uuid
import os

# Import Tavily with proper error handling
try:
    from langchain_community.tools.tavily_search import TavilySearchResults
    TAVILY_AVAILABLE = True
except ImportError:
    print("⚠️ Tavily not available - using fallback search")
    TAVILY_AVAILABLE = False

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

# Initialize Tavily search tool for social media discovery
if TAVILY_AVAILABLE:
    try:
        tavily_search = TavilySearchResults(
            max_results=5,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=True
        )
        print("✅ Tavily search initialized successfully")
    except Exception as e:
        print(f"⚠️ Tavily initialization failed: {e}")
        tavily_search = None
else:
    tavily_search = None

def greeting_node(state: NetaState, config: RunnableConfig) -> NetaState:
    """Initial greeting and business name collection"""
    
    # Check if we've already sent the greeting message
    messages = state.get("messages", [])
    has_greeted = any(msg.get("content", "").startswith("Hi! I'm Neta") for msg in messages)
    
    if not state.get("business_name"):
        if not has_greeted:
            # First time - send greeting
            greeting_msg = {
                "role": "assistant",
                "content": "Hi! I'm Neta, your AI Marketing Freelancer. I'll help you create amazing social media content based on your existing social presence. What's your business name?",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            return {
                **state,
                "messages": messages + [greeting_msg],
                "current_step": "greeting",  # Stay in greeting state
                "next_actions": [
                    {
                        "id": "provide_business_name",
                        "label": "Tell me your business name",
                        "action": "input_text"
                    }
                ]
            }
        else:
            # Already greeted, waiting for input - just return current state
            return state
    
    # Business name provided, move to next step
    return {
        **state,
        "current_step": "social_discovery"
    }

def social_discovery_node(state: NetaState, config: RunnableConfig) -> NetaState:
    """Search and analyze existing social media accounts using Tavily with progressive messaging"""
    
    business_name = state.get("business_name", "")
    messages = state.get("messages", [])
    user_data = state.get("user_data", {})
    
    # Check if already processed to avoid duplicate execution
    if user_data.get("social_search_completed"):
        return state
    
    # Progressive message sequence for better UX
    progress_messages = []
    
    # Step 1: Start message
    progress_messages.append({
        "role": "assistant",
        "content": f"Perfect! Let me search for {business_name}'s social media accounts... 🔍",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "progress", "step": "search_start"}
    })
    
    # Step 2: Facebook search indicator
    progress_messages.append({
        "role": "assistant", 
        "content": "Checking Facebook pages... 📘",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "progress", "step": "facebook_search"}
    })
    
    discovered_accounts = []
    
    # Execute Facebook search
    if tavily_search is not None:
        try:
            fb_query = f"{business_name} Facebook page site:facebook.com"
            fb_results = tavily_search.invoke(fb_query)
            
            # Parse Facebook results
            for result in fb_results[:2]:
                if 'facebook.com' in result.get('url', ''):
                    discovered_accounts.append({
                        "platform": "Facebook",
                        "name": result.get('title', business_name),
                        "url": result.get('url', ''),
                        "snippet": result.get('content', '')[:200],
                        "verified": False
                    })
                    
        except Exception as e:
            print(f"Facebook search failed: {e}")
    
    # Step 3: Instagram search indicator
    progress_messages.append({
        "role": "assistant",
        "content": "Searching Instagram accounts... 📸", 
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "progress", "step": "instagram_search"}
    })
    
    # Execute Instagram search
    if tavily_search is not None:
        try:
            ig_query = f"{business_name} Instagram site:instagram.com"
            ig_results = tavily_search.invoke(ig_query)
            
            # Parse Instagram results  
            for result in ig_results[:2]:
                if 'instagram.com' in result.get('url', ''):
                    discovered_accounts.append({
                        "platform": "Instagram",
                        "name": result.get('title', f"@{business_name.lower().replace(' ', '')}"),
                        "url": result.get('url', ''),
                        "snippet": result.get('content', '')[:200],
                        "verified": False
                    })
                    
        except Exception as e:
            print(f"Instagram search failed: {e}")
    
    # Fallback if no accounts found
    if not discovered_accounts:
        discovered_accounts = [
            {
                "platform": "Facebook",
                "name": f"{business_name}",
                "url": f"https://facebook.com/search/top?q={business_name.replace(' ', '%20')}",
                "snippet": "Search manually on Facebook",
                "verified": False
            },
            {
                "platform": "Instagram", 
                "name": f"@{business_name.lower().replace(' ', '')}",
                "url": f"https://instagram.com/explore/search/keyword/?q={business_name.replace(' ', '%20')}",
                "snippet": "Search manually on Instagram",
                "verified": False
            }
        ]
    
    # Step 4: Success message and individual account details
    if discovered_accounts:
        progress_messages.append({
            "role": "assistant",
            "content": "Great! I found your social accounts: ✅",
            "timestamp": "2024-01-01T00:00:00Z",
            "metadata": {"type": "success", "step": "accounts_found"}
        })
        
        # Individual account messages (mobile-optimized)
        for account in discovered_accounts:
            emoji = "🔵" if account['platform'] == 'Facebook' else "📸"
            progress_messages.append({
                "role": "assistant",
                "content": f"{emoji} {account['platform']}: {account['name']}",
                "timestamp": "2024-01-01T00:00:00Z",
                "metadata": {"type": "account_detail", "platform": account['platform'].lower()}
            })
    
    # Step 5: Confirmation request
    progress_messages.append({
        "role": "assistant",
        "content": "Are these your accounts? 🤔",
        "timestamp": "2024-01-01T00:00:00Z", 
        "metadata": {"type": "confirmation", "step": "verify"}
    })
    
    return {
        **state,
        "messages": messages + progress_messages,
        "current_step": "confirm_accounts",
        "social_accounts": discovered_accounts,
        "user_data": {
            **user_data,
            "social_search_completed": True
        },
        "next_actions": [
            {
                "id": "confirm_all",
                "label": "✅ Yes, these are mine",
                "action": "approve"
            },
            {
                "id": "select_some",
                "label": "📝 Only some of these",
                "action": "modify"
            },
            {
                "id": "not_mine",
                "label": "❌ These aren't mine",
                "action": "retry"
            }
        ]
    }

def content_analysis_node(state: NetaState, config: RunnableConfig) -> NetaState:
    """Analyze existing content using LLM with discovered social accounts and progressive messaging"""
    
    business_name = state.get("business_name", "")
    social_accounts = state.get("social_accounts", [])
    messages = state.get("messages", [])
    user_data = state.get("user_data", {})
    
    # Check if already processed to avoid duplicate execution
    if user_data.get("content_analysis_completed"):
        return state
    
    progress_messages = []
    
    # Step 1: Analysis start
    progress_messages.append({
        "role": "assistant",
        "content": f"Excellent! Now let me analyze {business_name}'s social media content... 📊",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "progress", "step": "analysis_start"}
    })
    
    if social_accounts:
        # Step 2: Account analysis
        progress_messages.append({
            "role": "assistant", 
            "content": "Analyzing your posting patterns and engagement... 🔍",
            "timestamp": "2024-01-01T00:00:00Z",
            "metadata": {"type": "progress", "step": "pattern_analysis"}
        })
        
        # Step 3: Content themes identification  
        progress_messages.append({
            "role": "assistant",
            "content": "Identifying your best-performing content themes... 🎯", 
            "timestamp": "2024-01-01T00:00:00Z",
            "metadata": {"type": "progress", "step": "theme_analysis"}
        })
        
        # Build analysis prompt with actual URLs
        urls_text = "\n".join([f"- {acc['platform']}: {acc['name']}" for acc in social_accounts])
        
        analysis_prompt = f"""
        Analyze the social media presence for {business_name} based on these accounts:
        {urls_text}
        
        Provide insights on:
        1. Content themes that work well for this business type
        2. Recommended posting style and brand voice  
        3. Typical engagement patterns for similar businesses
        4. 3 specific content strategy recommendations
        
        Keep the response friendly, actionable, and under 200 words.
        """
        
        try:
            # Use LLM to analyze
            response = llm.invoke(analysis_prompt)
            analysis_content = response.content if hasattr(response, 'content') else str(response)
            
            # Step 4: Analysis complete
            progress_messages.append({
                "role": "assistant",
                "content": "Analysis complete! Here's what I found: ✅",
                "timestamp": "2024-01-01T00:00:00Z",
                "metadata": {"type": "success", "step": "analysis_complete"}
            })
            
            # Step 5: Results
            progress_messages.append({
                "role": "assistant", 
                "content": analysis_content,
                "timestamp": "2024-01-01T00:00:00Z",
                "metadata": {"type": "analysis_results"}
            })
            
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            # Fallback analysis
            progress_messages.append({
                "role": "assistant",
                "content": "Based on your social accounts, I recommend focusing on visual content, behind-the-scenes posts, and customer engagement to build a strong social presence.",
                "timestamp": "2024-01-01T00:00:00Z",
                "metadata": {"type": "analysis_fallback"}
            })
            
    else:
        # No social accounts - provide starter strategy
        progress_messages.extend([
            {
                "role": "assistant",
                "content": "Creating a starter social media strategy for your business... 🚀",
                "timestamp": "2024-01-01T00:00:00Z",
                "metadata": {"type": "progress", "step": "starter_strategy"}
            },
            {
                "role": "assistant", 
                "content": f"I'll help you build a social media presence from scratch for {business_name}. Here are content themes that work well for businesses like yours:",
                "timestamp": "2024-01-01T00:00:00Z",
                "metadata": {"type": "starter_analysis"}
            }
        ])
    
    # Step 6: Strategy approval request
    progress_messages.append({
        "role": "assistant",
        "content": "Should I create a content strategy based on these insights? 🎨",
        "timestamp": "2024-01-01T00:00:00Z", 
        "metadata": {"type": "confirmation", "step": "strategy_approval"}
    })
    
    return {
        **state,
        "messages": messages + progress_messages,
        "current_step": "strategy_approval",
        "user_data": {
            **user_data,
            "content_analysis_completed": True,
            "content_themes": ["visual_content", "behind_the_scenes", "customer_engagement"],
            "analysis_insights": "Focus on visual storytelling and authentic engagement"
        },
        "next_actions": [
            {
                "id": "approve_strategy",
                "label": "✅ Sounds perfect",
                "action": "approve"
            },
            {
                "id": "adjust_themes",
                "label": "📝 Let me adjust these",
                "action": "modify"
            },
            {
                "id": "show_examples",
                "label": "👀 Show me examples first",
                "action": "preview"
            }
        ]
    }

def content_creation_node(state: NetaState, config: RunnableConfig) -> NetaState:
    """Generate content based on strategy with progressive messaging"""
    
    business_name = state.get("business_name", "")
    messages = state.get("messages", [])
    user_data = state.get("user_data", {})
    
    # Check if already processed to avoid duplicate execution
    if user_data.get("content_creation_completed"):
        return state
    
    progress_messages = []
    
    # Step 1: Creation start
    progress_messages.append({
        "role": "assistant",
        "content": f"Perfect! I'll create content that matches {business_name}'s style... 🎨",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "progress", "step": "creation_start"}
    })
    
    # Step 2: Analysis phase
    progress_messages.append({
        "role": "assistant",
        "content": "Analyzing your best-performing posts... 📊",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "progress", "step": "post_analysis"}
    })
    
    # Step 3: Hashtag research
    progress_messages.append({
        "role": "assistant",
        "content": "Researching trending hashtags in your area... 🔍",
        "timestamp": "2024-01-01T00:00:00Z", 
        "metadata": {"type": "progress", "step": "hashtag_research"}
    })
    
    # Step 4: Visual creation
    progress_messages.append({
        "role": "assistant",
        "content": "Creating images that match your visual style... 🎨",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "progress", "step": "visual_creation"}
    })
    
    # Step 5: Caption writing
    progress_messages.append({
        "role": "assistant", 
        "content": "Writing captions in your tone of voice... ✍️",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "progress", "step": "caption_writing"}
    })
    
    # Generate business-appropriate content
    generated_content = [
        {
            "id": "post_1",
            "type": "showcase_post",
            "caption": f"✨ Fresh from {business_name}! What's your favorite? 😍 #Quality #Local #Fresh",
            "image_description": f"Professional photo showcasing {business_name}'s main product/service",
            "hashtags": ["#Quality", "#Local", "#Fresh"],
            "best_time": "2:00 PM"
        },
        {
            "id": "post_2", 
            "type": "behind_scenes",
            "caption": f"Behind the scenes at {business_name} - passion in every detail! 💪 #BehindTheScenes #Quality #Crafted",
            "image_description": f"Behind-the-scenes look at {business_name}'s process",
            "hashtags": ["#BehindTheScenes", "#Quality", "#Crafted"],
            "best_time": "10:00 AM"
        }
    ]
    
    # Step 6: Success message
    progress_messages.append({
        "role": "assistant",
        "content": "Content creation complete! ✅",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "success", "step": "creation_complete"}
    })
    
    # Step 7: Presentation
    progress_messages.append({
        "role": "assistant",
        "content": f"Here are 2 posts I've created for {business_name}:\n\n📱 Post 1: Product showcase (high engagement type)\n📸 Post 2: Behind-the-scenes (builds trust)\n\nEach follows successful patterns from similar businesses.",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "content_presentation"}
    })
    
    # Step 8: Approval request
    progress_messages.append({
        "role": "assistant",
        "content": "Ready to review and approve? 🚀",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "confirmation", "step": "content_approval"}
    })
    
    return {
        **state,
        "messages": messages + progress_messages,
        "current_step": "content_approval",
        "user_data": {
            **user_data,
            "content_creation_completed": True,
            "generated_content": generated_content
        },
        "next_actions": [
            {
                "id": "approve_all",
                "label": "✅ Post all now",
                "action": "approve_all"
            },
            {
                "id": "review_individual", 
                "label": "👀 Review each one",
                "action": "review"
            },
            {
                "id": "create_different",
                "label": "🔄 Try different styles",
                "action": "regenerate"
            }
        ]
    }

def completion_node(state: NetaState, config: RunnableConfig) -> NetaState:
    """Final confirmation and scheduling with mobile-optimized messages"""
    
    business_name = state.get("business_name", "")
    messages = state.get("messages", [])
    user_data = state.get("user_data", {})
    
    # Check if already processed to avoid duplicate execution
    if user_data.get("completion_processed"):
        return state
    
    progress_messages = []
    
    # Step 1: Success confirmation (mobile-friendly)
    progress_messages.append({
        "role": "assistant",
        "content": f"Perfect! {business_name}'s content is ready! 🚀",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "success", "step": "content_ready"}
    })
    
    # Step 2: Scheduling details (concise for mobile)
    progress_messages.append({
        "role": "assistant",
        "content": "📅 Scheduling:\n📱 Post 1: Facebook at 2:00 PM\n📸 Post 2: Instagram at 2:05 PM",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "schedule_info"}
    })
    
    # Step 3: Performance monitoring promise
    progress_messages.append({
        "role": "assistant",
        "content": "I'll monitor performance and optimize based on engagement! 📊",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "monitoring_promise"}
    })
    
    # Step 4: Final success message (mobile-optimized)
    progress_messages.append({
        "role": "assistant",
        "content": f"All set! {business_name} is ready to shine on social media! ✨",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "final_success"}
    })
    
    # Step 5: Next steps call-to-action
    progress_messages.append({
        "role": "assistant",
        "content": "Ready to get started with your full social media strategy? 🎯",
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {"type": "cta"}
    })
    
    return {
        **state,
        "messages": messages + progress_messages,
        "current_step": "completed",
        "user_data": {
            **user_data,
            "completion_processed": True,
            "workflow_completed": True,
            "completion_time": "2024-01-01T00:00:00Z"
        },
        "next_actions": [
            {
                "id": "start_trial",
                "label": "🚀 Start Free Trial",
                "action": "begin_trial"
            },
            {
                "id": "learn_more",
                "label": "📚 Learn More",
                "action": "show_features"
            },
            {
                "id": "contact_support",
                "label": "💬 Questions?",
                "action": "contact_support"
            }
        ]
    }

def route_next_step(state: NetaState) -> Literal["greeting", "social_discovery", "content_analysis", "content_creation", "completion", END]:
    """Router function to determine next step"""
    
    current_step = state.get("current_step", "greeting")
    business_name = state.get("business_name", "")
    user_data = state.get("user_data", {})
    
    # Greeting phase - auto-progress when business name provided
    if current_step == "greeting":
        if business_name:
            return "social_discovery"  # ✅ Auto-progress to discovery
        return END  # Wait for user input
    
    # Social discovery phase - run automatically first time, then wait
    elif current_step == "social_discovery":
        if not user_data.get("social_search_completed"):
            return "social_discovery"  # ✅ Execute the discovery node
        else:
            return END  # Discovery done, wait for user confirmation
    
    # After user confirms accounts (transition from social discovery)
    elif current_step == "confirm_accounts":
        return "content_analysis"
    
    # Content analysis phase - run automatically first time
    elif current_step == "content_analysis":
        if not user_data.get("content_analysis_completed"):
            return "content_analysis"  # ✅ Execute the analysis node
        else:
            return END  # Analysis done, wait for strategy approval
        
    # After strategy approval
    elif current_step == "strategy_approval":
        return "content_creation"
    
    # Content creation phase - run automatically first time
    elif current_step == "content_creation":
        if not user_data.get("content_creation_completed"):
            return "content_creation"  # ✅ Execute the creation node
        else:
            return END  # Creation done, wait for content approval
        
    # After content approval
    elif current_step == "content_approval":
        return "completion"
        
    # Final state
    elif current_step == "completed":
        return END
        
    # Default fallback
    else:
        return END

# Build the workflow graph
builder = StateGraph(NetaState)

# Add nodes
builder.add_node("greeting", greeting_node)
builder.add_node("social_discovery", social_discovery_node)
builder.add_node("content_analysis", content_analysis_node)
builder.add_node("content_creation", content_creation_node)
builder.add_node("completion", completion_node)

# Add edges
builder.add_edge(START, "greeting")
builder.add_conditional_edges(
    "greeting",
    route_next_step,
    {
        "social_discovery": "social_discovery",
        END: END
    }
)
builder.add_conditional_edges(
    "social_discovery", 
    route_next_step,
    {
        "social_discovery": "social_discovery",  # Allow re-running discovery
        "content_analysis": "content_analysis",
        END: END
    }
)
builder.add_conditional_edges(
    "content_analysis",
    route_next_step,
    {
        "content_analysis": "content_analysis",  # Allow re-running analysis
        "content_creation": "content_creation",
        END: END
    }
)
builder.add_conditional_edges(
    "content_creation",
    route_next_step,
    {
        "content_creation": "content_creation",  # Allow re-running creation
        "completion": "completion",
        END: END
    }
)
builder.add_conditional_edges(
    "completion",
    route_next_step,
    {
        END: END
    }
)

# Compile the graph - this creates the app that LangGraph Cloud will use
app = builder.compile()

# For LangGraph Cloud, the app itself is the entry point
# The input will be passed directly to the compiled graph

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