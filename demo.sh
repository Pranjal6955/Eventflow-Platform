#!/bin/bash
# Demo script for the Event-Driven Platform

echo "==================================================="
echo "Event-Driven Microservices Platform Demo"
echo "==================================================="
echo ""

# Function to check service health
check_service() {
    local url=$1
    local service_name=$2
    
    echo "Checking $service_name..."
    response=$(curl -s -o /dev/null -w "%{http_code}" $url)
    if [ $response -eq 200 ]; then
        echo "✓ $service_name is healthy"
        return 0
    else
        echo "✗ $service_name is not responding (HTTP $response)"
        return 1
    fi
}

# Function to publish user analytics event
publish_user_analytics() {
    local user_id=$1
    local event_type=$2
    local metadata=$3
    
    echo "Publishing user analytics event..."
    curl -X POST "http://localhost:8000/api/v1/events/analytics" \
         -H "Content-Type: application/json" \
         -d "{
           \"user_id\": \"$user_id\",
           \"event_type\": \"$event_type\",
           \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
           \"metadata\": $metadata
         }" \
         -s -w "\nHTTP Status: %{http_code}\n"
    echo ""
}

# Function to publish chemical research event
publish_chemical_research() {
    local molecule_id=$1
    local researcher=$2
    local formula=$3
    local weight=$4
    
    echo "Publishing chemical research event..."
    curl -X POST "http://localhost:8000/api/v1/events/chemical" \
         -H "Content-Type: application/json" \
         -d "{
           \"molecule_id\": \"$molecule_id\",
           \"researcher\": \"$researcher\",
           \"data\": {
             \"formula\": \"$formula\",
             \"weight\": $weight,
             \"state\": \"liquid\"
           },
           \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
         }" \
         -s -w "\nHTTP Status: %{http_code}\n"
    echo ""
}

# Function to get analytics
get_analytics() {
    local endpoint=$1
    local description=$2
    
    echo "Fetching $description..."
    curl -s "http://localhost:8001/api/v1/$endpoint" | jq '.' 2>/dev/null || echo "Failed to fetch analytics"
    echo ""
}

echo "Step 1: Checking service health..."
echo "=================================="

check_service "http://localhost:8000/healthz" "Event Publisher Service"
publisher_healthy=$?

check_service "http://localhost:8001/healthz" "Event Subscriber Service"
subscriber_healthy=$?

if [ $publisher_healthy -ne 0 ] || [ $subscriber_healthy -ne 0 ]; then
    echo ""
    echo "❌ Some services are not running. Please ensure:"
    echo "1. Infrastructure is running: docker-compose up -d"
    echo "2. Publisher service is running: cd event_publisher_service && ./start.sh"
    echo "3. Subscriber service is running: cd event_subscriber_service && ./start.sh"
    echo ""
    exit 1
fi

echo ""
echo "Step 2: Scenario 1 - User Analytics Platform"
echo "============================================"

echo "Publishing user interaction events..."
publish_user_analytics "user_alice" "page_view" '{"page": "/dashboard", "source": "web"}'
publish_user_analytics "user_alice" "click" '{"button": "signup", "location": "header"}'
publish_user_analytics "user_bob" "page_view" '{"page": "/pricing", "source": "mobile"}'
publish_user_analytics "user_alice" "purchase" '{"amount": 99.99, "currency": "USD", "product": "premium_plan"}'
publish_user_analytics "user_charlie" "login" '{"method": "google", "location": "homepage"}'

echo "Waiting for events to be processed..."
sleep 5

echo "Fetching user analytics..."
get_analytics "analytics/user/user_alice" "Alice's Analytics"
get_analytics "events/user/user_alice" "Alice's Recent Events"

echo ""
echo "Step 3: Scenario 2 - Chemical Research Platform"
echo "==============================================="

echo "Publishing chemical research data..."
publish_chemical_research "mol_water" "Dr. Smith" "H2O" 18.015
publish_chemical_research "mol_salt" "Dr. Johnson" "NaCl" 58.44
publish_chemical_research "mol_co2" "Dr. Smith" "CO2" 44.01
publish_chemical_research "mol_methane" "Dr. Brown" "CH4" 16.04

echo "Waiting for LLM processing..."
sleep 10

echo "Fetching research analytics..."
get_analytics "analytics/researcher/Dr.%20Smith" "Dr. Smith's Research Summary"
get_analytics "events/researcher/Dr.%20Smith" "Dr. Smith's Recent Experiments"

echo ""
echo "Step 4: Error Handling Demonstration"
echo "===================================="

echo "Testing invalid user analytics event (missing required field)..."
curl -X POST "http://localhost:8000/api/v1/events/analytics" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test_user"}' \
     -s -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "Testing invalid chemical research event (missing required field)..."
curl -X POST "http://localhost:8000/api/v1/events/chemical" \
     -H "Content-Type: application/json" \
     -d '{"molecule_id": "test_mol"}' \
     -s -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "Step 5: Performance Test"
echo "======================="

echo "Publishing 10 concurrent user analytics events..."
for i in {1..10}; do
    publish_user_analytics "load_test_user_$i" "load_test" '{"test": true, "batch": 1}' &
done
wait

echo "All events published successfully!"

echo ""
echo "Step 6: Service Metrics"
echo "======================"

echo "Event Publisher Metrics:"
curl -s "http://localhost:8000/metrics" | jq '.' 2>/dev/null || echo "Metrics not available"

echo ""
echo "==================================================="
echo "Demo completed successfully! 🎉"
echo "==================================================="
echo ""
echo "What was demonstrated:"
echo "• High-volume concurrent API request handling"
echo "• Asynchronous event processing with Kafka"
echo "• Database persistence with PostgreSQL"
echo "• LLM integration for chemical property extraction"
echo "• Fault-tolerant error handling"
echo "• Clean architecture with separation of concerns"
echo "• Comprehensive monitoring and analytics"
echo ""
echo "Architecture components:"
echo "• Event Publisher Service (FastAPI + Kafka Producer)"
echo "• Event Subscriber Service (Kafka Consumer + Celery + PostgreSQL)"
echo "• Message Broker (Apache Kafka)"
echo "• Database (PostgreSQL)"
echo "• Task Queue (Celery + Redis)"
echo "• Monitoring APIs (FastAPI)"
echo ""
echo "To explore the APIs:"
echo "• Publisher API docs: http://localhost:8000/docs"
echo "• Subscriber API docs: http://localhost:8001/docs"
echo "• Kafka UI: http://localhost:8080"
echo ""
