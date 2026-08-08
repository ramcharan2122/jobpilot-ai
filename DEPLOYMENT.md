# JobPilot AI — GitHub & Render Deployment Guide

Follow this guide to deploy JobPilot AI to GitHub and launch it on Render / Vercel.

---

## Step 1: Initialize Git & Push to GitHub

1. Open your terminal in the workspace directory:
   ```bash
   cd "/Users/shashikiranreddy/Desktop/job search"
   ```

2. Initialize Git and commit all files:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Production JobPilot AI Mass Job Application Platform"
   ```

3. Create a new public or private repository on GitHub (e.g., `jobpilot-ai`).

4. Connect your local repository and push:
   ```bash
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/jobpilot-ai.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 2: Deploy to Render (Blueprint Automatic Setup)

1. Log in to [Render.com](https://render.com).
2. Click **New +** -> select **Blueprints**.
3. Connect your `jobpilot-ai` GitHub repository.
4. Render will automatically read `render.yaml` and configure:
   - **`jobpilot-backend`**: Python 3.12 Web Service running FastAPI.
   - **`jobpilot-frontend`**: Static Site hosting the React Vite SaaS frontend.
5. Click **Apply**. Render will build and deploy both services automatically!

---

## Step 3: Configure Environment Secrets (Optional)

In your Render Dashboard for `jobpilot-backend`, add Environment Variables under **Environment**:

```env
SECRET_KEY=generate_random_secret_jwt_key
AI_PROVIDER=OPENAI # Or GEMINI / SMART_MOCK
AI_API_KEY=your_openai_or_gemini_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

## Step 4: Live Production URLs

Once deployed on Render, your live production links will be:
- **Frontend SaaS Web Application**: `https://jobpilot-frontend.onrender.com`
- **Backend API & Swagger Docs**: `https://jobpilot-backend.onrender.com/docs`
