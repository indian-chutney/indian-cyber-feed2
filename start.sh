#!/bin/bash

# Indian Cyber Threat Intelligence Platform Startup Script
echo "=========================================="
echo "Indian Cyber Threat Intelligence Platform"
echo "=========================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists docker; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✅ Docker found"

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi
echo "✅ Docker Compose found"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from example..."
    cp config/.env.development .env
    echo "✅ .env file created from development template"
fi

# Start the platform
echo ""
echo "Starting the Indian Cyber Threat Intelligence Platform..."
echo "This will start:"
echo "  - PostgreSQL Database (port 5432)"
echo "  - Redis Cache (port 6379)"
echo "  - Backend API (port 8000)"
echo "  - Frontend Dashboard (port 3000)"
echo ""

# Build and start containers
docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Platform started successfully!"
    echo ""
    echo "Access URLs:"
    echo "  - Frontend Dashboard: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Documentation: http://localhost:8000/api/docs"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
else
    echo "❌ Failed to start the platform"
    exit 1
fi