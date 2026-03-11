#!/bin/bash

# Configuration
SERVER_IP="34.58.12.77"

echo "======================================"
echo "Starting Deployment on $SERVER_IP"
echo "======================================"

# Pull latest changes (if in a git repo)
# git pull origin master

# Build and start containers
docker-compose up -d --build

# Wait for backend to be ready
echo "Waiting for backend to start..."
sleep 5

# Run migrations
echo "Running database migrations..."
docker-compose exec -T backend python manage.py migrate

# Collect static files
echo "Collecting static files..."
docker-compose exec -T backend python manage.py collectstatic --noinput

echo "======================================"
echo "Deployment Complete!"
echo "URL: http://$SERVER_IP"
echo "======================================"
