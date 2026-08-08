#!/bin/bash

echo "🚀 Preparing JobPilot AI repository for GitHub and Render deployment..."

# Initialize git if not present
if [ ! -d ".git" ]; then
    git init
    echo "✓ Git repository initialized."
fi

git add .
git commit -m "Production JobPilot AI: Multi-Platform ATS Ingestion, 300 Apps/Day Engine, Render Blueprint"

echo ""
echo "✅ Local Git commit created!"
echo ""
echo "Next step: Run the following commands with your GitHub repository URL:"
echo "------------------------------------------------------------------"
echo "git remote add origin https://github.com/YOUR_USERNAME/jobpilot-ai.git"
echo "git branch -M main"
echo "git push -u origin main"
echo "------------------------------------------------------------------"
