#!/bin/bash

# Domain Deployment Script
# This script deploys your betting analytics app with domain support

DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"your-email@example.com"}

echo "🚀 Deploying Betting Analytics with Domain: $DOMAIN"
echo "📧 Email: $EMAIL"
echo ""

# Check if domain is provided
if [ "$DOMAIN" = "your-domain.com" ]; then
    echo "❌ Please provide your domain name!"
    echo "Usage: ./deploy-domain.sh your-domain.com your-email@example.com"
    exit 1
fi

# Check if email is provided
if [ "$EMAIL" = "your-email@example.com" ]; then
    echo "❌ Please provide your email address!"
    echo "Usage: ./deploy-domain.sh your-domain.com your-email@example.com"
    exit 1
fi

echo "📋 Step 1: Updating configuration files..."
# Update nginx.conf with your domain
sed -i "s/your-domain.com/$DOMAIN/g" nginx.conf

# Update docker-compose file with your domain
sed -i "s/your-domain.com/$DOMAIN/g" docker-compose.domain.yml

echo "📋 Step 2: Building and starting services..."
# Build and start services
docker-compose -f docker-compose.domain.yml build
docker-compose -f docker-compose.domain.yml up -d

echo "📋 Step 3: Setting up SSL certificates..."
# Make SSL setup script executable and run it
chmod +x setup-ssl.sh
./setup-ssl.sh $DOMAIN $EMAIL

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your site should be available at: https://$DOMAIN"
echo "📊 API endpoint: https://$DOMAIN/api"
echo ""
echo "📝 Next steps:"
echo "1. Update your DNS settings on Hostinger to point to your server IP"
echo "2. Wait for DNS propagation (can take up to 24 hours)"
echo "3. Test your site at https://$DOMAIN"
echo ""
echo "🔧 Useful commands:"
echo "- View logs: docker-compose -f docker-compose.domain.yml logs -f"
echo "- Restart services: docker-compose -f docker-compose.domain.yml restart"
echo "- Update database: docker-compose -f docker-compose.domain.yml --profile update up db-updater"
echo "- Run database update script: docker-compose -f docker-compose.domain.yml run --rm betting-analytics ./update_database.sh" 