# Deploying to Vercel

This guide will help you deploy your LangGraph Agent API to Vercel.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. Your code pushed to a GitHub repository
3. An OpenAI API key

## Deployment Steps

### 1. Push to GitHub

Make sure your code is pushed to a GitHub repository with the following structure:
```
project/
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── agent.py
│   ├── chat.py
│   ├── tools.py
│   └── index.py
├── public/
│   └── index.html
├── vercel.json
├── requirements.txt
└── DEPLOYMENT.md
```

### 2. Deploy to Vercel

1. **Login to Vercel**: Go to [vercel.com](https://vercel.com) and log in
2. **New Project**: Click "New Project"
3. **Import Repository**: Connect your GitHub account and select your repository
4. **Configure Project**:
   - Framework Preset: "Other"
   - Root Directory: "./" (leave as default)
   - Build Command: Leave empty (Vercel will auto-detect)
   - Output Directory: Leave empty
   - Install Command: Leave empty

### 3. Environment Variables

Before deploying, add your environment variables:

1. In the Vercel dashboard, go to your project settings
2. Click on "Environment Variables"
3. Add the following variable:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: Your OpenAI API key
   - **Environment**: Production (and optionally Preview/Development)

### 4. Deploy

Click "Deploy" and wait for the deployment to complete.

## Vercel Configuration

The `vercel.json` file configures how Vercel handles your FastAPI application:

```json
{
    "builds": [
        {
            "src": "api/main.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "api/main.py"
        }
    ]
}
```

## Testing Your Deployment

Once deployed, you can test your API:

1. **Root endpoint**: `https://your-app.vercel.app/` - Should serve your frontend
2. **Health check**: `https://your-app.vercel.app/health` - API health status
3. **API docs**: `https://your-app.vercel.app/docs` - FastAPI auto-generated docs
4. **Chat endpoint**: `https://your-app.vercel.app/chat` - POST endpoint for chat

## Environment Variables Required

- `OPENAI_API_KEY`: Your OpenAI API key (required for the agent to function)

## Troubleshooting

### Common Issues

1. **Deployment fails**: Check that all dependencies are listed in `requirements.txt`
2. **Import errors**: Ensure all relative imports in the `api/` directory use dot notation (e.g., `from .tools import`)
3. **Static files not found**: The app will gracefully degrade to JSON responses if static files aren't found

### Node.js Version

If you encounter deployment issues, try changing the Node.js version:
1. Go to your project settings in Vercel
2. Scroll to "Node.js Version"  
3. Change it to 18.x
4. Redeploy

## API Usage

The deployed API provides several endpoints:

- `GET /` - Frontend interface
- `GET /health` - Health check with detailed status
- `GET /tools` - List available tools
- `POST /chat` - Chat with the agent

### Chat API Example

```bash
curl -X POST "https://your-app.vercel.app/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What is the weather in New York?",
       "openai_api_key": "your-api-key-here"
     }'
```

Or include the API key in environment variables and just send:

```bash
curl -X POST "https://your-app.vercel.app/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What is the weather in New York?"
     }'
``` 