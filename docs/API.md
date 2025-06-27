# API Documentation

## Event Publisher Service API

**Base URL**: `http://localhost:8000`

### Authentication
Currently, no authentication is required for the publisher service. In production, consider implementing API key authentication.

### Common Headers
```
Content-Type: application/json
Accept: application/json
```

### Response Format
All responses follow a consistent JSON format:

**Success Response:**
```json
{
  "message": "Event published"
}
```

**Error Response:**
```json
{
  "detail": "Error description",
  "error": "Technical error details"
}
```

---

## Endpoints

### 1. Health Check

**GET** `/healthz`

Check if the service is running and healthy.

**Response:**
```json
{
  "status": "ok",
  "service": "event_publisher",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 2. Service Metrics

**GET** `/metrics`

Get basic service metrics and information.

**Response:**
```json
{
  "service": "event_publisher",
  "status": "running",
  "version": "1.0.0",
  "uptime": "N/A"
}
```

**Status Codes:**
- `200 OK` - Metrics retrieved successfully

---

### 3. Publish User Analytics Event

**POST** `/api/v1/events/analytics`

Publish a user analytics event for processing.

**Request Body:**
```json
{
  "user_id": "string",           // Required: User identifier
  "event_type": "string",        // Required: Type of event (e.g., "page_view", "click", "purchase")
  "timestamp": "string",         // Required: ISO 8601 timestamp
  "metadata": {                  // Optional: Additional event data
    "page": "/dashboard",
    "source": "web",
    "session_id": "abc123",
    "user_agent": "Mozilla/5.0..."
  }
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/events/analytics" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_12345",
    "event_type": "page_view",
    "timestamp": "2024-01-01T12:00:00Z",
    "metadata": {
      "page": "/dashboard",
      "source": "web",
      "referrer": "https://google.com"
    }
  }'
```

**Response:**
```json
{
  "message": "Event published"
}
```

**Status Codes:**
- `202 Accepted` - Event published successfully
- `422 Unprocessable Entity` - Invalid request data
- `500 Internal Server Error` - Service error

**Event Types:**
- `page_view` - User viewed a page
- `click` - User clicked an element
- `purchase` - User made a purchase
- `login` - User logged in
- `logout` - User logged out
- `signup` - User signed up
- `search` - User performed a search

---

### 4. Publish Chemical Research Event

**POST** `/api/v1/events/chemical`

Publish a chemical research event for processing and LLM analysis.

**Request Body:**
```json
{
  "molecule_id": "string",       // Required: Unique molecule identifier
  "researcher": "string",        // Required: Researcher name or ID
  "data": {                      // Required: Chemical data
    "formula": "H2O",
    "weight": 18.015,
    "state": "liquid",
    "temperature": 25,
    "pressure": 1.0,
    "purity": 99.9
  },
  "timestamp": "string"          // Required: ISO 8601 timestamp
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/events/chemical" \
  -H "Content-Type: application/json" \
  -d '{
    "molecule_id": "mol_water_001",
    "researcher": "Dr. Jane Smith",
    "data": {
      "formula": "H2O",
      "weight": 18.015,
      "state": "liquid",
      "temperature": 25,
      "pressure": 1.0,
      "purity": 99.9,
      "synthesis_method": "distillation"
    },
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

**Response:**
```json
{
  "message": "Event published"
}
```

**Status Codes:**
- `202 Accepted` - Event published successfully
- `422 Unprocessable Entity` - Invalid request data
- `500 Internal Server Error` - Service error

---

## Event Subscriber Service API

**Base URL**: `http://localhost:8001`

### Authentication
Currently, no authentication is required. Consider implementing authentication for production use.

---

## Monitoring Endpoints

### 1. Health Check

**GET** `/healthz`

Check if the subscriber service is running and healthy.

**Response:**
```json
{
  "status": "ok",
  "service": "event_subscriber"
}
```

---

### 2. User Analytics Summary

**GET** `/api/v1/analytics/user/{user_id}`

Get analytics summary for a specific user.

**Parameters:**
- `user_id` (path) - User identifier

**Example Request:**
```bash
curl "http://localhost:8001/api/v1/analytics/user/user_12345"
```

**Response:**
```json
{
  "user_id": "user_12345",
  "total_events": 25,
  "event_types": {
    "page_view": 15,
    "click": 8,
    "purchase": 2
  },
  "recent_events": [
    {
      "id": "event_uuid",
      "event_type": "page_view",
      "timestamp": "2024-01-01T12:00:00Z",
      "metadata": {
        "page": "/dashboard"
      },
      "processed_at": "2024-01-01T12:00:01Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Analytics retrieved successfully
- `404 Not Found` - User not found
- `500 Internal Server Error` - Service error

---

### 3. Researcher Analytics Summary

**GET** `/api/v1/analytics/researcher/{researcher}`

Get research summary for a specific researcher.

**Parameters:**
- `researcher` (path) - Researcher name or ID (URL encoded)

**Example Request:**
```bash
curl "http://localhost:8001/api/v1/analytics/researcher/Dr.%20Jane%20Smith"
```

**Response:**
```json
{
  "researcher": "Dr. Jane Smith",
  "total_experiments": 12,
  "unique_molecules": 8,
  "molecules_list": [
    "mol_water_001",
    "mol_salt_002",
    "mol_co2_003"
  ],
  "recent_experiments": [
    {
      "id": "experiment_uuid",
      "molecule_id": "mol_water_001",
      "data": {
        "formula": "H2O",
        "weight": 18.015
      },
      "llm_properties": {
        "color": "colorless",
        "ph": 7.0,
        "confidence_score": 0.95
      },
      "timestamp": "2024-01-01T12:00:00Z",
      "processed_at": "2024-01-01T12:00:02Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Analytics retrieved successfully
- `404 Not Found` - Researcher not found
- `500 Internal Server Error` - Service error

---

### 4. User Events

**GET** `/api/v1/events/user/{user_id}`

Get recent events for a specific user.

**Parameters:**
- `user_id` (path) - User identifier
- `limit` (query, optional) - Number of events to return (default: 10, max: 100)

**Example Request:**
```bash
curl "http://localhost:8001/api/v1/events/user/user_12345?limit=20"
```

**Response:**
```json
{
  "user_id": "user_12345",
  "events": [
    {
      "id": "event_uuid_1",
      "user_id": "user_12345",
      "event_type": "page_view",
      "timestamp": "2024-01-01T12:00:00Z",
      "metadata": {
        "page": "/dashboard",
        "source": "web"
      },
      "processed_at": "2024-01-01T12:00:01Z"
    },
    {
      "id": "event_uuid_2",
      "user_id": "user_12345",
      "event_type": "click",
      "timestamp": "2024-01-01T12:01:00Z",
      "metadata": {
        "button": "signup",
        "location": "header"
      },
      "processed_at": "2024-01-01T12:01:01Z"
    }
  ]
}
```

---

### 5. Researcher Events

**GET** `/api/v1/events/researcher/{researcher}`

Get recent experiments for a specific researcher.

**Parameters:**
- `researcher` (path) - Researcher name or ID (URL encoded)
- `limit` (query, optional) - Number of events to return (default: 10, max: 100)

**Example Request:**
```bash
curl "http://localhost:8001/api/v1/events/researcher/Dr.%20Jane%20Smith?limit=5"
```

**Response:**
```json
{
  "researcher": "Dr. Jane Smith",
  "events": [
    {
      "id": "experiment_uuid_1",
      "molecule_id": "mol_water_001",
      "researcher": "Dr. Jane Smith",
      "data": {
        "formula": "H2O",
        "weight": 18.015,
        "state": "liquid"
      },
      "timestamp": "2024-01-01T12:00:00Z",
      "llm_properties": {
        "color": "colorless",
        "ph": 7.0,
        "boiling_point": "100°C",
        "confidence_score": 0.95,
        "analysis_timestamp": "2024-01-01T12:00:01Z"
      },
      "processed_at": "2024-01-01T12:00:02Z"
    }
  ]
}
```

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Human-readable error message",
  "error": "Technical error details (optional)",
  "timestamp": "2024-01-01T12:00:00Z",
  "path": "/api/v1/events/analytics"
}
```

### Common Error Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| `400 Bad Request` | Invalid request | Malformed JSON or invalid parameters |
| `422 Unprocessable Entity` | Validation error | Request data doesn't match expected schema |
| `500 Internal Server Error` | Server error | Unexpected server-side error |
| `503 Service Unavailable` | Service unavailable | Service temporarily unavailable |

### Validation Errors

For `422` status codes, the response includes detailed validation information:

```json
{
  "detail": [
    {
      "loc": ["body", "user_id"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "timestamp"],
      "msg": "invalid datetime format",
      "type": "value_error.datetime"
    }
  ]
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production deployment, consider:

- API rate limiting (requests per minute/hour)
- User-based rate limiting
- IP-based rate limiting
- Burst capacity management

---

## OpenAPI Documentation

Interactive API documentation is available at:

- **Publisher Service**: http://localhost:8000/docs
- **Subscriber Service**: http://localhost:8001/docs

These provide:
- Interactive API testing
- Request/response schemas
- Example requests
- Authentication information

---

## SDK Examples

### Python SDK Example

```python
import httpx
import asyncio
from datetime import datetime

class EventPublisherClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def publish_analytics_event(self, user_id: str, event_type: str, metadata: dict = None):
        payload = {
            "user_id": user_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {}
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/events/analytics",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def publish_chemical_event(self, molecule_id: str, researcher: str, data: dict):
        payload = {
            "molecule_id": molecule_id,
            "researcher": researcher,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/events/chemical",
            json=payload
        )
        response.raise_for_status()
        return response.json()

# Usage
async def main():
    client = EventPublisherClient()
    
    # Publish analytics event
    await client.publish_analytics_event(
        user_id="user_123",
        event_type="page_view",
        metadata={"page": "/dashboard"}
    )
    
    # Publish chemical research event
    await client.publish_chemical_event(
        molecule_id="mol_water",
        researcher="Dr. Smith",
        data={"formula": "H2O", "weight": 18.015}
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript/Node.js SDK Example

```javascript
const axios = require('axios');

class EventPublisherClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    async publishAnalyticsEvent(userId, eventType, metadata = {}) {
        const payload = {
            user_id: userId,
            event_type: eventType,
            timestamp: new Date().toISOString(),
            metadata: metadata
        };

        const response = await this.client.post('/api/v1/events/analytics', payload);
        return response.data;
    }

    async publishChemicalEvent(moleculeId, researcher, data) {
        const payload = {
            molecule_id: moleculeId,
            researcher: researcher,
            data: data,
            timestamp: new Date().toISOString()
        };

        const response = await this.client.post('/api/v1/events/chemical', payload);
        return response.data;
    }
}

// Usage
const client = new EventPublisherClient();

client.publishAnalyticsEvent('user_123', 'page_view', { page: '/dashboard' })
    .then(result => console.log('Analytics event published:', result))
    .catch(error => console.error('Error:', error));
```

This API documentation provides comprehensive information for integrating with the Event-Driven Platform, including examples, error handling, and SDK implementations.
