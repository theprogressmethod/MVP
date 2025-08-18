#!/bin/bash

# Environment Switcher Script for The Progress Method
# Usage: ./scripts/switch-env.sh [dev|staging|prod]

ENV=$1

if [ -z "$ENV" ]; then
    echo "Usage: ./scripts/switch-env.sh [dev|staging|prod]"
    echo "Current branch: $(git branch --show-current)"
    exit 1
fi

case $ENV in
    dev)
        echo "🔄 Switching to DEVELOPMENT environment..."
        
        # Switch git branch
        git checkout dev || git checkout -b dev
        
        # Copy development env file
        if [ -f .env.development ]; then
            cp .env.development .env.local
            echo "✅ Development environment variables loaded"
        else
            echo "⚠️  .env.development not found. Please configure your dev environment."
        fi
        
        # Update package.json scripts for dev
        echo "📦 Configured for development mode"
        echo "🌿 Git branch: dev"
        echo "🔗 Render config: render-dev.yaml"
        echo ""
        echo "To deploy to Render dev:"
        echo "  render up --file render-dev.yaml"
        ;;
        
    staging)
        echo "🔄 Switching to STAGING environment..."
        
        # Switch git branch
        git checkout staging || git checkout -b staging
        
        # Copy staging env file
        if [ -f .env.staging ]; then
            cp .env.staging .env.local
            echo "✅ Staging environment variables loaded"
        else
            echo "⚠️  .env.staging not found. Please configure your staging environment."
        fi
        
        echo "📦 Configured for staging mode"
        echo "🌿 Git branch: staging"
        echo "🔗 Render config: render.yaml"
        ;;
        
    prod)
        echo "🔄 Switching to PRODUCTION environment..."
        
        # Switch git branch
        git checkout main
        
        # Copy production env file
        if [ -f .env.production ]; then
            cp .env.production .env.local
            echo "✅ Production environment variables loaded"
        else
            echo "⚠️  .env.production not found. Please configure your production environment."
        fi
        
        echo "📦 Configured for production mode"
        echo "🌿 Git branch: main"
        echo "🔗 Render config: render-prod.yaml"
        ;;
        
    *)
        echo "❌ Invalid environment. Use: dev, staging, or prod"
        exit 1
        ;;
esac

echo ""
echo "🚀 Environment switch complete!"
echo ""
echo "Next steps:"
echo "1. Update .env.local with your actual credentials"
echo "2. Run 'npm run dev' to start local development"
echo "3. Commit and push changes to trigger deployment"