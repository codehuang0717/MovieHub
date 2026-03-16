#!/bin/bash

# Configuration
SERVER_IP="34.58.12.77"
# Stop script on first error
set -e

echo "======================================"
echo "Starting Deployment on $SERVER_IP"
echo "======================================"

# 1. Pull latest changes
echo "Pulling latest code..."
git pull origin master

# 2. Force rebuild and recreate containers
# --no-cache ensures Docker doesn't use old build layers
echo "Building new containers..."
docker-compose build --no-cache

echo "Starting containers..."
docker-compose up -d

# 3. Run migrations
echo "Running database migrations..."
docker-compose exec -T backend python manage.py migrate

# 4. Restart Nginx to force it to reload fresh static files from the volume
echo "Restarting Nginx..."
docker-compose restart nginx

echo "======================================"
echo "Deployment Complete!"
echo "URL: http://$SERVER_IP"
echo "======================================"
