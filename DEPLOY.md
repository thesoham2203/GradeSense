# Quick Deploy to Get Public URL

## 🌐 Get Public API URL in 5 Minutes

Choose one of these deployment options to get a public URL for your GradeSense API:

## Option 1: Railway (Recommended - Free Tier)

### Step 1: Prepare for Railway

```bash
# Create railway.json
echo '{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}' > railway.json
```

### Step 2: Deploy

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Select your GradeSense repository
5. Add environment variables:
   - `GEMINI_API_KEY=your_key_here`
   - `PORT=8000`
6. Deploy!

**Result**: `https://your-app.railway.app`

---

## Option 2: Render (Free Tier)

### Step 1: Create render.yaml

```yaml
services:
  - type: web
    name: gradesense-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.11
      - key: GEMINI_API_KEY
        value: your_api_key_here
```

### Step 2: Deploy

1. Go to [render.com](https://render.com)
2. Connect GitHub account
3. Create new Web Service
4. Select repository
5. Deploy!

**Result**: `https://your-app.onrender.com`

---

## Option 3: Heroku (Free tier discontinued, but reliable)

### Step 1: Create Procfile

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Step 2: Create runtime.txt

```
python-3.10.11
```

### Step 3: Deploy

```bash
# Install Heroku CLI
# Login and create app
heroku create your-gradesense-api
heroku config:set GEMINI_API_KEY=your_key_here
git push heroku main
```

**Result**: `https://your-gradesense-api.herokuapp.com`

---

## Option 4: Vercel (Serverless)

### Step 1: Create vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ]
}
```

### Step 2: Deploy

```bash
npx vercel --prod
```

**Result**: `https://your-app.vercel.app`

---

## Option 5: Google Cloud Run (Pay-as-you-go)

### Step 1: Build and deploy

```bash
gcloud run deploy gradesense-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key_here
```

**Result**: `https://gradesense-api-xxx.a.run.app`

---

## 🚀 Fastest Option: Railway

1. **Push to GitHub** (if not already)
2. **Go to [railway.app](https://railway.app)**
3. **Connect GitHub and deploy**
4. **Add your Gemini API key**
5. **Get instant public URL!**

## 📋 What You'll Get

Once deployed, your public API will have:

- **📚 Public Docs**: `https://your-url.com/docs`
- **🔗 API Base**: `https://your-url.com`
- **❤️ Health Check**: `https://your-url.com/api/v1/health`
- **📄 ReDoc**: `https://your-url.com/redoc`

## 🔑 Remember to Set Environment Variables

```env
GEMINI_API_KEY=your_actual_api_key
OPENAI_API_KEY=your_openai_key (optional)
API_KEYS=your-secure-api-key
LLM_PROVIDER=gemini
```

## 🎯 Need Help?

Choose **Railway** for the easiest deployment - it's free and takes 2 minutes!
