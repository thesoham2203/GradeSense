#!/bin/bash

# 🚀 One-Click Deploy Script for GradeSense API

echo "🎯 GradeSense API - Quick Deploy"
echo "================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - GradeSense API"
fi

echo ""
echo "🌐 Choose your deployment platform:"
echo "1. Railway (Recommended - Free, Fast)"
echo "2. Render (Free tier available)"
echo "3. Vercel (Serverless, Free)"
echo "4. Heroku (Paid plans available)"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🚂 Deploying to Railway..."
        echo ""
        echo "1. Go to https://railway.app"
        echo "2. Sign up with GitHub"
        echo "3. Click 'Deploy from GitHub repo'"
        echo "4. Select your GradeSense repository"
        echo "5. Add environment variable: GEMINI_API_KEY"
        echo ""
        echo "✅ Your API will be available at: https://your-app.railway.app"
        echo "📚 Docs will be at: https://your-app.railway.app/docs"
        ;;
    2)
        echo "🎨 Deploying to Render..."
        echo ""
        echo "1. Go to https://render.com"
        echo "2. Connect your GitHub account"
        echo "3. Create new Web Service"
        echo "4. Select your repository"
        echo "5. Use these settings:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
        echo "6. Add environment variable: GEMINI_API_KEY"
        echo ""
        echo "✅ Your API will be available at: https://your-app.onrender.com"
        echo "📚 Docs will be at: https://your-app.onrender.com/docs"
        ;;
    3)
        echo "⚡ Deploying to Vercel..."
        echo ""
        echo "1. Install Vercel CLI: npm i -g vercel"
        echo "2. Run: vercel --prod"
        echo "3. Follow the prompts"
        echo "4. Add environment variable: GEMINI_API_KEY in dashboard"
        echo ""
        echo "✅ Your API will be available at: https://your-app.vercel.app"
        echo "📚 Docs will be at: https://your-app.vercel.app/docs"
        ;;
    4)
        echo "🟣 Deploying to Heroku..."
        echo ""
        echo "1. Install Heroku CLI"
        echo "2. Run: heroku login"
        echo "3. Run: heroku create your-gradesense-api"
        echo "4. Run: heroku config:set GEMINI_API_KEY=your_key_here"
        echo "5. Run: git push heroku main"
        echo ""
        echo "✅ Your API will be available at: https://your-gradesense-api.herokuapp.com"
        echo "📚 Docs will be at: https://your-gradesense-api.herokuapp.com/docs"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🔑 Don't forget to:"
echo "1. Add your Gemini API key to environment variables"
echo "2. Test your deployment at /health endpoint"
echo "3. Check the interactive docs at /docs"
echo ""
echo "🎉 Happy deploying!"
