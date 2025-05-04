#!/bin/bash
# Local deployment script for Voice AI Restaurant Agent

set -e  # Exit immediately if a command exits with a non-zero status

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Display header
echo "=================================================="
echo "Voice AI Restaurant Agent - Local Deployment"
echo "=================================================="

# Check if .env file exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "Creating .env file from .env.example..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo "Please edit .env file with your configuration values"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create storage directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/storage"

cd "$PROJECT_ROOT"

# Build and start containers
echo "Building and starting containers..."
docker-compose -f infrastructure/local/docker-compose.yml up --build -d

# Get the container ID
CONTAINER_ID=$(docker-compose -f infrastructure/local/docker-compose.yml ps -q app)

# Get the ngrok public URL
echo "Waiting for ngrok to start..."
sleep 5
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | grep -o 'http[^"]*')

if [ -z "$NGROK_URL" ]; then
    echo "Warning: Could not get ngrok URL. Please check if ngrok is running properly."
    echo "You can manually check the ngrok URL at http://localhost:4040"
else
    echo "=================================================="
    echo "Ngrok URL: $NGROK_URL"
    echo "Use this URL in your Twilio webhook configuration."
    echo "=================================================="
fi

# Display application logs
echo "Displaying application logs (press Ctrl+C to exit)..."
docker logs -f $CONTAINER_ID