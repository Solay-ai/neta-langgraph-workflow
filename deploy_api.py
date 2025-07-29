#!/usr/bin/env python3
"""
Deploy Neta Social Assistant to LangGraph Platform via API
"""
import requests
import json
import os
import zipfile
from pathlib import Path

# Configuration
LANGSMITH_API_KEY = "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"
DEPLOYMENT_NAME = "neta-social-assistant"
LANGSMITH_BASE_URL = "https://api.smith.langchain.com"

def create_deployment_package():
    """Create a ZIP package of the workflow"""
    print("📦 Creating deployment package...")
    
    # Files to include
    files_to_zip = [
        "neta_social_assistant.py",
        "langgraph.json", 
        "requirements.txt",
        ".env"
    ]
    
    # Create ZIP file
    zip_path = "neta-deployment.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files_to_zip:
            if os.path.exists(file):
                zipf.write(file)
                print(f"  ✅ Added {file}")
            else:
                print(f"  ⚠️ Skipped {file} (not found)")
    
    return zip_path

def deploy_to_langgraph_platform():
    """Deploy to LangGraph Platform"""
    print("🚀 Deploying to LangGraph Platform...")
    
    headers = {
        "Authorization": f"Bearer {LANGSMITH_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Try different potential API endpoints
    potential_endpoints = [
        f"{LANGSMITH_BASE_URL}/deployments",
        f"{LANGSMITH_BASE_URL}/v1/deployments", 
        f"{LANGSMITH_BASE_URL}/langgraph/deployments",
        f"{LANGSMITH_BASE_URL}/assistants",
        f"{LANGSMITH_BASE_URL}/v1/assistants"
    ]
    
    deployment_data = {
        "name": DEPLOYMENT_NAME,
        "description": "Neta AI Marketing Freelancer for social media automation",
        "config": {
            "graph": "neta_social_assistant.py:app",
            "dependencies": [
                "langgraph>=0.2.0",
                "langchain-openai>=0.1.0", 
                "langchain-core>=0.3.0"
            ]
        }
    }
    
    for endpoint in potential_endpoints:
        print(f"🔗 Trying endpoint: {endpoint}")
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=deployment_data,
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code in [200, 201]:
                print("✅ Deployment successful!")
                return response.json()
            elif response.status_code == 404:
                print("   ❌ Endpoint not found, trying next...")
                continue
            else:
                print(f"   ⚠️ Unexpected response: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    print("❌ All endpoints failed. Manual deployment required.")
    return None

def test_deployment():
    """Test the deployed assistant"""
    print("🧪 Testing deployment...")
    
    headers = {
        "Authorization": f"Bearer {LANGSMITH_API_KEY}",
        "Content-Type": "application/json"
    }
    
    test_data = {
        "assistant_id": DEPLOYMENT_NAME,
        "input": {
            "business_name": "Test Business",
            "messages": [],
            "current_step": "greeting",
            "user_data": {}
        }
    }
    
    test_endpoints = [
        f"{LANGSMITH_BASE_URL}/threads/test/runs",
        f"{LANGSMITH_BASE_URL}/runs"
    ]
    
    for endpoint in test_endpoints:
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=test_data,
                timeout=30
            )
            
            print(f"Test endpoint: {endpoint}")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code in [200, 201]:
                print("✅ Test successful!")
                return True
                
        except Exception as e:
            print(f"Test error: {e}")
    
    return False

if __name__ == "__main__":
    print("🌟 LangGraph Platform Deployment Script")
    print("=" * 50)
    
    # Step 1: Create package
    zip_path = create_deployment_package()
    
    # Step 2: Deploy
    result = deploy_to_langgraph_platform()
    
    # Step 3: Test if deployment succeeded
    if result:
        test_deployment()
    
    # Cleanup
    if os.path.exists(zip_path):
        os.remove(zip_path)
        print(f"🧹 Cleaned up {zip_path}")
    
    print("\n📋 Next Steps:")
    print("1. If API deployment failed, use the LangSmith web console")
    print("2. Go to https://smith.langchain.com/")
    print("3. Navigate to Deployments → Create New")
    print("4. Upload the workflow files")
    print("5. Set assistant name to 'neta-social-assistant'")