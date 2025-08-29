@echo off
echo 🎯 GradeSense API - Quick Deploy
echo =================================

REM Check if git is initialized
if not exist ".git" (
    echo 📦 Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit - GradeSense API"
)

echo.
echo 🌐 Choose your deployment platform:
echo 1. Railway ^(Recommended - Free, Fast^)
echo 2. Render ^(Free tier available^)
echo 3. Vercel ^(Serverless, Free^)
echo 4. Heroku ^(Paid plans available^)
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto railway
if "%choice%"=="2" goto render
if "%choice%"=="3" goto vercel
if "%choice%"=="4" goto heroku
goto invalid

:railway
echo 🚂 Deploying to Railway...
echo.
echo 1. Go to https://railway.app
echo 2. Sign up with GitHub
echo 3. Click 'Deploy from GitHub repo'
echo 4. Select your GradeSense repository
echo 5. Add environment variable: GEMINI_API_KEY
echo.
echo ✅ Your API will be available at: https://your-app.railway.app
echo 📚 Docs will be at: https://your-app.railway.app/docs
goto end

:render
echo 🎨 Deploying to Render...
echo.
echo 1. Go to https://render.com
echo 2. Connect your GitHub account
echo 3. Create new Web Service
echo 4. Select your repository
echo 5. Use these settings:
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
echo 6. Add environment variable: GEMINI_API_KEY
echo.
echo ✅ Your API will be available at: https://your-app.onrender.com
echo 📚 Docs will be at: https://your-app.onrender.com/docs
goto end

:vercel
echo ⚡ Deploying to Vercel...
echo.
echo 1. Install Vercel CLI: npm i -g vercel
echo 2. Run: vercel --prod
echo 3. Follow the prompts
echo 4. Add environment variable: GEMINI_API_KEY in dashboard
echo.
echo ✅ Your API will be available at: https://your-app.vercel.app
echo 📚 Docs will be at: https://your-app.vercel.app/docs
goto end

:heroku
echo 🟣 Deploying to Heroku...
echo.
echo 1. Install Heroku CLI
echo 2. Run: heroku login
echo 3. Run: heroku create your-gradesense-api
echo 4. Run: heroku config:set GEMINI_API_KEY=your_key_here
echo 5. Run: git push heroku main
echo.
echo ✅ Your API will be available at: https://your-gradesense-api.herokuapp.com
echo 📚 Docs will be at: https://your-gradesense-api.herokuapp.com/docs
goto end

:invalid
echo ❌ Invalid choice. Please run the script again.
goto :eof

:end
echo.
echo 🔑 Don't forget to:
echo 1. Add your Gemini API key to environment variables
echo 2. Test your deployment at /health endpoint
echo 3. Check the interactive docs at /docs
echo.
echo 🎉 Happy deploying!
pause
