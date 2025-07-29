# 🚀 LangGraph Cloud Deployment Instructions

## Repository Information
- **GitHub**: https://github.com/Solay-ai/neta-langgraph-workflow
- **Assistant ID**: `neta-social-assistant`
- **API Key**: `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`

## 🌐 Deploy to LangGraph Cloud

### Step 1: Access LangSmith Console
1. Go to: **https://smith.langchain.com/**
2. Sign in with your API key: `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`

### Step 2: Create New Deployment
1. Click **"Deployments"** in the left sidebar
2. Click **"+ New Deployment"** button
3. Select **"From GitHub"**

### Step 3: Configure Deployment
- **Repository**: `Solay-ai/neta-langgraph-workflow`
- **Branch**: `main`
- **Assistant Name**: `neta-social-assistant`
- **Description**: Neta AI Marketing Freelancer
- **Environment Variables**:
  - `OPENAI_API_KEY`: [Your OpenAI API key]
  - `LANGCHAIN_API_KEY`: `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`

### Step 4: Deploy
1. Click **"Deploy"**
2. Wait for build to complete
3. Note the deployment URL

### Step 5: Test Deployment
```bash
curl -X POST "https://[your-deployment-url]/runs/stream" \
  -H "Authorization: Bearer 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" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "neta-social-assistant",
    "input": {
      "business_name": "Mike'\''s Pizza",
      "messages": [],
      "current_step": "greeting"
    }
  }'
```

## 🔄 Update Your App

Once deployed, update `src/langgraph/cloud/client.ts`:

```typescript
const LANGGRAPH_API_URL = 'https://[your-deployment-url]'; // Replace with actual URL
```

## ✅ Expected Results

After successful deployment:
- ✅ Real LangGraph Cloud execution
- ✅ No more 404 errors
- ✅ Full Neta AI freelancer experience
- ✅ Scalable cloud infrastructure

## 🆘 Support

If you encounter issues:
1. Check deployment logs in LangSmith console
2. Verify environment variables are set
3. Confirm GitHub repository access
4. Test with simple input first