#!/bin/bash

# SSL Certificate Setup Script
# This script sets up SSL certificates using Let's Encrypt

DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"your-email@example.com"}

echo "Setting up SSL certificates for $DOMAIN"
echo "Email: $EMAIL"

# Create necessary directories
mkdir -p ssl
mkdir -p logs/nginx

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    sudo apt update
    sudo apt install -y certbot
fi

# Stop nginx temporarily for certificate generation
echo "Stopping nginx temporarily..."
docker-compose -f docker-compose.domain.yml stop nginx

# Generate SSL certificate
echo "Generating SSL certificate..."
sudo certbot certonly --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Copy certificates to our ssl directory
echo "Copying certificates..."
sudo cp -r /etc/letsencrypt/live/$DOMAIN ./ssl/
sudo chown -R $USER:$USER ./ssl/

# Update nginx.conf with your domain
echo "Updating nginx configuration..."
sed -i "s/your-domain.com/$DOMAIN/g" nginx.conf

# Start the services
echo "Starting services..."
docker-compose -f docker-compose.domain.yml up -d

echo "SSL setup complete!"
echo "Your site should now be available at https://$DOMAIN"
echo ""
echo "To renew certificates automatically, add this to your crontab:"
echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose -f docker-compose.domain.yml restart nginx" 