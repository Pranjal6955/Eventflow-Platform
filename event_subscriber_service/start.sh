#!/bin/bash
# Startup script for Event Subscriber Service

echo "Starting Event Subscriber Service..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

echo "Virtual environment activated: $VIRTUAL_ENV"

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify key packages are installed
python -c "import fastapi; import celery; import confluent_kafka; print('All key packages installed successfully')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: Failed to install required packages"
    exit 1
fi

# Check if infrastructure is available
echo "Checking infrastructure connectivity..."

# Check Kafka
timeout 10 bash -c 'until echo > /dev/tcp/localhost/9092; do sleep 1; done' 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Kafka is available"
else
    echo "✗ Warning: Kafka is not available at localhost:9092"
fi

# Check PostgreSQL
timeout 10 bash -c 'until echo > /dev/tcp/localhost/5432; do sleep 1; done' 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ PostgreSQL is available"
else
    echo "✗ Warning: PostgreSQL is not available at localhost:5432"
fi

# Check Redis
timeout 10 bash -c 'until echo > /dev/tcp/localhost/6379; do sleep 1; done' 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Redis is available"
else
    echo "✗ Warning: Redis is not available at localhost:6379"
fi

echo ""
echo "Infrastructure check complete. Make sure to start with: docker-compose up -d"
echo ""

# Function to start Celery worker
start_celery_worker() {
    echo "Starting Celery worker..."
    celery -A app.api_worker.handlers:app worker --loglevel=info --concurrency=2 &
    CELERY_PID=$!
    echo "Celery worker started with PID: $CELERY_PID"
}

# Function to start Kafka consumer
start_kafka_consumer() {
    echo "Starting Kafka consumer..."
    python -m app.main_worker &
    CONSUMER_PID=$!
    echo "Kafka consumer started with PID: $CONSUMER_PID"
}

# Function to start monitoring API
start_monitoring_api() {
    echo "Starting monitoring API on port 8001..."
    uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 1 &
    API_PID=$!
    echo "Monitoring API started with PID: $API_PID"
}

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down services..."
    if [ ! -z "$CELERY_PID" ]; then
        kill $CELERY_PID 2>/dev/null
        echo "Stopped Celery worker"
    fi
    if [ ! -z "$CONSUMER_PID" ]; then
        kill $CONSUMER_PID 2>/dev/null
        echo "Stopped Kafka consumer"
    fi
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        echo "Stopped monitoring API"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check command line argument
if [ "$1" = "worker-only" ]; then
    echo "Starting worker components only..."
    start_celery_worker
    start_kafka_consumer
elif [ "$1" = "api-only" ]; then
    echo "Starting API only..."
    start_monitoring_api
else
    echo "Starting all components..."
    start_celery_worker
    sleep 2
    start_kafka_consumer
    sleep 2
    start_monitoring_api
fi

echo ""
echo "Event Subscriber Service is running!"
echo "- Celery worker: Active"
echo "- Kafka consumer: Active"
echo "- Monitoring API: http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all background processes
wait
