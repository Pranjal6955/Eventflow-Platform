# Event-Driven Platform Demo

This document provides step-by-step curl commands to demonstrate the functionality of the Event-Driven Platform.

## Prerequisites

1. Ensure both services are running:
   - Publisher Service: `http://localhost:8000`
   - Subscriber Service: `http://localhost:8001`

2. Open two terminal windows for better visibility of the demo flow.

---

## Step 1: Health Checks

First, let's verify both services are running properly.

### Check Publisher Service Health
```bash
curl -X GET "http://localhost:8000/healthz" \
  -H "Accept: application/json"
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "event_publisher",
  "version": "1.0.0"
}
```

### Check Subscriber Service Health
```bash
curl -X GET "http://localhost:8001/healthz" \
  -H "Accept: application/json"
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "event_subscriber"
}
```

---

## Step 2: Service Metrics

Get basic service information and metrics.

### Publisher Service Metrics
```bash
curl -X GET "http://localhost:8000/metrics" \
  -H "Accept: application/json"
```

**Expected Response:**
```json
{
  "service": "event_publisher",
  "status": "running",
  "version": "1.0.0",
  "uptime": "N/A"
}
```

---

## Step 3: User Analytics Events Demo

Let's simulate a user journey with multiple analytics events.

### 3.1: User Page View Event
```bash
curl -X POST "http://localhost:8000/api/v1/events/analytics" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "user_id": "demo_user_001",
    "event_type": "page_view",
    "timestamp": "2024-01-01T10:00:00Z",
    "metadata": {
      "page": "/home",
      "source": "web",
      "session_id": "session_abc123",
      "user_agent": "Mozilla/5.0 (demo browser)"
    }
  }'
```

### 3.2: User Login Event
```bash
curl -X POST "http://localhost:8000/api/v1/events/analytics" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "user_id": "demo_user_001",
    "event_type": "login",
    "timestamp": "2024-01-01T10:01:00Z",
    "metadata": {
      "source": "web",
      "method": "email",
      "session_id": "session_abc123"
    }
  }'
```

### 3.3: User Dashboard View
```bash
curl -X POST "http://localhost:8000/api/v1/events/analytics" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "user_id": "demo_user_001",
    "event_type": "page_view",
    "timestamp": "2024-01-01T10:02:00Z",
    "metadata": {
      "page": "/dashboard",
      "source": "web",
      "session_id": "session_abc123",
      "referrer": "/home"
    }
  }'
```

### 3.4: User Click Event
```bash
curl -X POST "http://localhost:8000/api/v1/events/analytics" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "user_id": "demo_user_001",
    "event_type": "click",
    "timestamp": "2024-01-01T10:03:00Z",
    "metadata": {
      "element": "upgrade_button",
      "page": "/dashboard",
      "position": "header",
      "session_id": "session_abc123"
    }
  }'
```

### 3.5: User Search Event
```bash
curl -X POST "http://localhost:8000/api/v1/events/analytics" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "user_id": "demo_user_001",
    "event_type": "search",
    "timestamp": "2024-01-01T10:04:00Z",
    "metadata": {
      "query": "chemical analysis tools",
      "results_count": 25,
      "page": "/search",
      "session_id": "session_abc123"
    }
  }'
```

**Expected Response for all analytics events:**
```json
{
  "message": "Event published"
}
```

---

## Step 4: Chemical Research Events Demo

Now let's simulate chemical research activities.

### 4.1: Water Analysis Experiment
```bash
curl -X POST "http://localhost:8000/api/v1/events/chemical" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "molecule_id": "demo_water_h2o",
    "researcher": "Dr. Demo Scientist",
    "data": {
      "formula": "H2O",
      "weight": 18.015,
      "state": "liquid",
      "temperature": 25.0,
      "pressure": 1.0,
      "purity": 99.9,
      "ph": 7.0,
      "synthesis_method": "distillation"
    },
    "timestamp": "2024-01-01T11:00:00Z"
  }'
```

### 4.2: Salt Analysis Experiment
```bash
curl -X POST "http://localhost:8000/api/v1/events/chemical" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "molecule_id": "demo_salt_nacl",
    "researcher": "Dr. Demo Scientist",
    "data": {
      "formula": "NaCl",
      "weight": 58.44,
      "state": "solid",
      "temperature": 20.0,
      "pressure": 1.0,
      "purity": 98.5,
      "crystal_structure": "cubic",
      "solubility": "high in water"
    },
    "timestamp": "2024-01-01T11:15:00Z"
  }'
```

### 4.3: Carbon Dioxide Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/events/chemical" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "molecule_id": "demo_co2_carbon_dioxide",
    "researcher": "Dr. Demo Scientist",
    "data": {
      "formula": "CO2",
      "weight": 44.01,
      "state": "gas",
      "temperature": 25.0,
      "pressure": 1.0,
      "density": 1.977,
      "greenhouse_potential": "high",
      "source": "combustion analysis"
    },
    "timestamp": "2024-01-01T11:30:00Z"
  }'
```

### 4.4: Ethanol Analysis by Different Researcher
```bash
curl -X POST "http://localhost:8000/api/v1/events/chemical" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "molecule_id": "demo_ethanol_c2h6o",
    "researcher": "Dr. Jane Research",
    "data": {
      "formula": "C2H6O",
      "weight": 46.07,
      "state": "liquid",
      "temperature": 20.0,
      "pressure": 1.0,
      "purity": 95.0,
      "boiling_point": 78.37,
      "flash_point": 13.0,
      "application": "solvent analysis"
    },
    "timestamp": "2024-01-01T11:45:00Z"
  }'
```

**Expected Response for all chemical events:**
```json
{
  "message": "Event published"
}
```

---

## Step 5: Query Analytics Data

After publishing events, let's retrieve the processed analytics data.

⚠️ **Note**: Wait 10-15 seconds after publishing events to allow processing time.

### 5.1: Get User Analytics Summary
```bash
curl -X GET "http://localhost:8001/api/v1/analytics/user/demo_user_001" \
  -H "Accept: application/json"
```

**Expected Response:**
```json
{
  "user_id": "demo_user_001",
  "total_events": 5,
  "event_types": {
    "page_view": 2,
    "login": 1,
    "click": 1,
    "search": 1
  },
  "recent_events": [
    {
      "id": "event_uuid",
      "event_type": "search",
      "timestamp": "2024-01-01T10:04:00Z",
      "metadata": {
        "query": "chemical analysis tools"
      },
      "processed_at": "2024-01-01T10:04:01Z"
    }
  ]
}
```

### 5.2: Get Researcher Analytics Summary
```bash
curl -X GET "http://localhost:8001/api/v1/analytics/researcher/Dr.%20Demo%20Scientist" \
  -H "Accept: application/json"
```

**Expected Response:**
```json
{
  "researcher": "Dr. Demo Scientist",
  "total_experiments": 3,
  "unique_molecules": 3,
  "molecules_list": [
    "demo_water_h2o",
    "demo_salt_nacl",
    "demo_co2_carbon_dioxide"
  ],
  "recent_experiments": [
    {
      "id": "experiment_uuid",
      "molecule_id": "demo_co2_carbon_dioxide",
      "data": {
        "formula": "CO2",
        "weight": 44.01
      },
      "llm_properties": {
        "color": "colorless",
        "state_description": "gas at standard conditions",
        "confidence_score": 0.95
      },
      "timestamp": "2024-01-01T11:30:00Z",
      "processed_at": "2024-01-01T11:30:02Z"
    }
  ]
}
```

### 5.3: Get Recent User Events
```bash
curl -X GET "http://localhost:8001/api/v1/events/user/demo_user_001?limit=10" \
  -H "Accept: application/json"
```

### 5.4: Get Recent Researcher Events
```bash
curl -X GET "http://localhost:8001/api/v1/events/researcher/Dr.%20Demo%20Scientist?limit=5" \
  -H "Accept: application/json"
```

### 5.5: Get Events for Second Researcher
```bash
curl -X GET "http://localhost:8001/api/v1/events/researcher/Dr.%20Jane%20Research?limit=5" \
  -H "Accept: application/json"
```

---

## Step 6: Advanced Demo Scenarios

### 6.1: Simulate Multiple Users
Create events for additional users to see aggregate analytics:

```bash
# User 2 - Mobile user
curl -X POST "http://localhost:8000/api/v1/events/analytics" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_002",
    "event_type": "page_view",
    "timestamp": "2024-01-01T12:00:00Z",
    "metadata": {
      "page": "/mobile-app",
      "source": "mobile",
      "device": "iPhone",
      "session_id": "mobile_session_456"
    }
  }'

# User 2 - Purchase event
curl -X POST "http://localhost:8000/api/v1/events/analytics" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_002",
    "event_type": "purchase",
    "timestamp": "2024-01-01T12:05:00Z",
    "metadata": {
      "product": "premium_subscription",
      "amount": 29.99,
      "currency": "USD",
      "source": "mobile"
    }
  }'
```

### 6.2: Simulate Complex Chemical Research
```bash
# Complex organic molecule
curl -X POST "http://localhost:8000/api/v1/events/chemical" \
  -H "Content-Type: application/json" \
  -d '{
    "molecule_id": "demo_caffeine_complex",
    "researcher": "Dr. Organic Chemistry",
    "data": {
      "formula": "C8H10N4O2",
      "weight": 194.19,
      "state": "solid",
      "temperature": 25.0,
      "pressure": 1.0,
      "melting_point": 227.0,
      "solubility_water": "moderate",
      "pharmacology": "stimulant",
      "synthesis_route": "methylation of theobromine"
    },
    "timestamp": "2024-01-01T13:00:00Z"
  }'
```

---

## Step 7: Error Handling Demo

### 7.1: Invalid Request - Missing Required Field
```bash
curl -X POST "http://localhost:8000/api/v1/events/analytics" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "page_view",
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

**Expected Response (422 Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "user_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 7.2: Invalid Timestamp Format
```bash
curl -X POST "http://localhost:8000/api/v1/events/analytics" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "event_type": "page_view",
    "timestamp": "invalid-timestamp"
  }'
```

### 7.3: Query Non-existent User
```bash
curl -X GET "http://localhost:8001/api/v1/analytics/user/nonexistent_user" \
  -H "Accept: application/json"
```

**Expected Response (404 Error):**
```json
{
  "detail": "User not found"
}
```

---

## Demo Script Summary

This demo showcases:

1. **Service Health**: Both publisher and subscriber services are operational
2. **User Analytics**: Complete user journey from page views to searches
3. **Chemical Research**: Multiple experiments with LLM analysis integration
4. **Data Retrieval**: Querying processed analytics and research data
5. **Multiple Researchers**: Demonstrating data segregation by researcher
6. **Error Handling**: Proper validation and error responses

## Next Steps

1. **Monitor Logs**: Check service logs during the demo to see event processing
2. **Scale Testing**: Use these commands in loops to test with higher volumes
3. **Integration**: Use these examples to build client applications
4. **Production**: Implement proper authentication and rate limiting

## Automation Script

For automated testing, you can save all successful commands to a shell script:

```bash
#!/bin/bash
# demo-script.sh

echo "Starting Event-Driven Platform Demo..."

# Health checks
echo "1. Checking service health..."
curl -s "http://localhost:8000/healthz"
curl -s "http://localhost:8001/healthz"

# Publish events
echo "2. Publishing user events..."
# Add all the successful curl commands here

echo "Demo completed!"
```

Make it executable with: `chmod +x demo-script.sh`
