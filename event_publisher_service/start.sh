#!/bin/bash
# Startup script for Event Publisher Service

echo "Starting Event Publisher Service..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if Kafka is available
echo "Checking Kafka connectivity..."
timeout 10 bash -c 'until echo > /dev/tcp/localhost/9092; do sleep 1; done' 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Kafka is available"
else
    echo "Warning: Kafka is not available at localhost:9092"
    echo "Make sure to start the infrastructure with: docker-compose up -d"
fi

# Start the service
echo "Starting Event Publisher Service on port 8000..."
python -m app.main
