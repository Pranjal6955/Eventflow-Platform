# Testing Guide

## Overview

This guide covers the comprehensive testing strategy for the Event-Driven Microservices Platform, including unit tests, integration tests, and end-to-end testing.

## Testing Philosophy

The platform follows the **Test Pyramid** approach:
- **70% Unit Tests**: Fast, isolated tests for business logic
- **20% Integration Tests**: Tests for component interactions
- **10% End-to-End Tests**: Full workflow validation

## Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── test_models.py
│   ├── test_services.py
│   └── test_transformers.py
├── integration/          # Integration tests
│   ├── test_database.py
│   ├── test_kafka.py
│   └── test_api.py
├── e2e/                  # End-to-end tests
│   ├── test_workflows.py
│   └── test_scenarios.py
├── performance/          # Performance tests
│   ├── test_load.py
│   └── test_stress.py
└── fixtures/             # Test data
    ├── events.json
    └── schemas.json
```

---

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov httpx

# Start test infrastructure
docker-compose -f docker-compose.test.yml up -d
```

### Event Publisher Service Tests

```bash
cd event_publisher_service

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api_routes.py

# Run tests matching pattern
pytest -k "test_publish_user_analytics"

# Run tests with markers
pytest -m "unit"
pytest -m "integration"
```

### Event Subscriber Service Tests

```bash
cd event_subscriber_service

# Run all tests
pytest

# Run async tests
pytest tests/test_event_processing.py -v

# Run database tests (requires test DB)
pytest tests/test_database_repository.py --db-url=postgresql://test:test@localhost:5433/test_db

# Run integration tests
pytest tests/integration/ -v
```

---

## Unit Tests

### Publisher Service Unit Tests

#### API Models Tests
```python
# tests/unit/test_models.py
import pytest
from pydantic import ValidationError
from app.api.models import UserAnalyticsEvent, ChemicalResearchEvent

class TestUserAnalyticsEvent:
    def test_valid_event(self):
        event = UserAnalyticsEvent(
            user_id="user_123",
            event_type="page_view",
            timestamp="2024-01-01T12:00:00Z",
            metadata={"page": "/dashboard"}
        )
        assert event.user_id == "user_123"
        assert event.event_type == "page_view"
        assert event.metadata["page"] == "/dashboard"
    
    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            UserAnalyticsEvent(
                user_id="user_123",
                # Missing event_type
                timestamp="2024-01-01T12:00:00Z"
            )
    
    def test_invalid_timestamp(self):
        with pytest.raises(ValidationError):
            UserAnalyticsEvent(
                user_id="user_123",
                event_type="page_view",
                timestamp="invalid_timestamp"
            )

class TestChemicalResearchEvent:
    def test_valid_event(self):
        event = ChemicalResearchEvent(
            molecule_id="mol_123",
            researcher="Dr. Smith",
            data={"formula": "H2O", "weight": 18.015},
            timestamp="2024-01-01T12:00:00Z"
        )
        assert event.molecule_id == "mol_123"
        assert event.data["formula"] == "H2O"
    
    def test_empty_data_dict(self):
        # Should allow empty data dict
        event = ChemicalResearchEvent(
            molecule_id="mol_123",
            researcher="Dr. Smith",
            data={},
            timestamp="2024-01-01T12:00:00Z"
        )
        assert event.data == {}
```

#### Business Logic Tests
```python
# tests/unit/test_event_service.py
import pytest
from unittest.mock import Mock
from app.core.event_service import EventService

class TestEventService:
    def test_publish_event_success(self):
        # Arrange
        mock_queue = Mock()
        service = EventService(mock_queue)
        event_data = {"type": "test", "data": "sample"}
        
        # Act
        service.publish_event(event_data)
        
        # Assert
        mock_queue.enqueue.assert_called_once_with(event_data)
    
    def test_publish_event_queue_failure(self):
        # Arrange
        mock_queue = Mock()
        mock_queue.enqueue.side_effect = Exception("Queue error")
        service = EventService(mock_queue)
        event_data = {"type": "test", "data": "sample"}
        
        # Act & Assert
        with pytest.raises(Exception, match="Queue error"):
            service.publish_event(event_data)
```

### Subscriber Service Unit Tests

#### Event Processing Tests
```python
# tests/unit/test_event_processing.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.core.event_processing_service import EventProcessingService

class TestEventProcessingService:
    @pytest.fixture
    def mock_dependencies(self):
        database_repo = Mock()
        database_repo.save_user_analytics_event = AsyncMock(return_value="event_id")
        database_repo.create_event_processing_status = AsyncMock()
        database_repo.update_event_processing_status = AsyncMock()
        
        llm_service = Mock()
        llm_service.extract_chemical_properties = AsyncMock(return_value={
            "color": "blue", "ph": 7.0
        })
        
        return database_repo, llm_service
    
    @pytest.mark.asyncio
    async def test_process_user_analytics_event(self, mock_dependencies):
        # Arrange
        database_repo, llm_service = mock_dependencies
        service = EventProcessingService(database_repo, llm_service)
        
        event_data = {
            "user_id": "user_123",
            "event_type": "click",
            "timestamp": "2024-01-01T12:00:00Z",
            "metadata": {"button": "signup"}
        }
        
        # Act
        result = await service.process_user_analytics_event(event_data)
        
        # Assert
        assert result == "event_id"
        database_repo.save_user_analytics_event.assert_called_once_with(event_data)
        database_repo.create_event_processing_status.assert_called_once()
        database_repo.update_event_processing_status.assert_called_with(
            "event_id", "completed"
        )
    
    @pytest.mark.asyncio
    async def test_process_chemical_event_with_llm(self, mock_dependencies):
        # Arrange
        database_repo, llm_service = mock_dependencies
        service = EventProcessingService(database_repo, llm_service)
        
        event_data = {
            "molecule_id": "mol_123",
            "researcher": "Dr. Smith",
            "data": {"formula": "H2O"},
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        # Act
        result = await service.process_chemical_research_event(event_data)
        
        # Assert
        llm_service.extract_chemical_properties.assert_called_once_with(
            event_data["data"]
        )
        database_repo.save_chemical_research_event.assert_called_once()
        
        # Verify LLM properties were added
        saved_event = database_repo.save_chemical_research_event.call_args[0][0]
        assert "llm_properties" in saved_event
        assert saved_event["llm_properties"]["color"] == "blue"
```

---

## Integration Tests

### Database Integration Tests

```python
# tests/integration/test_database.py
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.infrastructure.postgresql_repository import PostgreSQLRepository
from app.infrastructure.database_models import Base

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create test database and tables."""
    # Use a separate test database
    test_db_url = "postgresql+asyncpg://postgres:password@localhost:5432/test_events_db"
    
    # Create tables
    sync_engine = create_engine(
        test_db_url.replace("+asyncpg", ""),
        echo=False
    )
    Base.metadata.create_all(sync_engine)
    
    yield test_db_url
    
    # Cleanup
    Base.metadata.drop_all(sync_engine)

@pytest.fixture
async def repository(test_db):
    """Create repository instance with test database."""
    # Mock settings for test
    import app.infrastructure.postgresql_repository as repo_module
    original_settings = repo_module.settings
    
    class TestSettings:
        POSTGRES_DSN = test_db
    
    repo_module.settings = TestSettings()
    
    repository = PostgreSQLRepository()
    yield repository
    
    # Restore original settings
    repo_module.settings = original_settings

class TestPostgreSQLRepository:
    @pytest.mark.asyncio
    async def test_save_and_retrieve_user_analytics_event(self, repository):
        # Arrange
        event_data = {
            "user_id": "test_user",
            "event_type": "page_view",
            "timestamp": "2024-01-01T12:00:00Z",
            "metadata": {"page": "/test"}
        }
        
        # Act - Save event
        event_id = await repository.save_user_analytics_event(event_data)
        
        # Act - Retrieve events
        events = await repository.get_user_analytics_events("test_user", 10)
        
        # Assert
        assert event_id is not None
        assert len(events) == 1
        assert events[0]["user_id"] == "test_user"
        assert events[0]["event_type"] == "page_view"
    
    @pytest.mark.asyncio
    async def test_save_chemical_research_event_with_llm_properties(self, repository):
        # Arrange
        event_data = {
            "molecule_id": "mol_test",
            "researcher": "Dr. Test",
            "data": {"formula": "H2O"},
            "timestamp": "2024-01-01T12:00:00Z",
            "llm_properties": {"color": "colorless", "ph": 7.0}
        }
        
        # Act
        event_id = await repository.save_chemical_research_event(event_data)
        events = await repository.get_chemical_research_events("Dr. Test", 10)
        
        # Assert
        assert event_id is not None
        assert len(events) == 1
        assert events[0]["llm_properties"]["color"] == "colorless"
        assert events[0]["llm_properties"]["ph"] == 7.0
```

### Kafka Integration Tests

```python
# tests/integration/test_kafka.py
import pytest
import json
import asyncio
from confluent_kafka import Consumer, Producer
from app.infrastructure.kafka_producer import KafkaEventQueue
from app.infrastructure.kafka_consumer import KafkaEventConsumer

class TestKafkaIntegration:
    @pytest.fixture
    def kafka_config(self):
        return {
            'bootstrap.servers': 'localhost:9092',
            'topic': 'test_events_topic'
        }
    
    @pytest.fixture
    def producer(self, kafka_config):
        return KafkaEventQueue(
            kafka_config['bootstrap.servers'],
            kafka_config['topic']
        )
    
    def test_produce_and_consume_message(self, kafka_config, producer):
        # Arrange
        test_event = {
            "type": "test_event",
            "user_id": "test_user",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        received_events = []
        
        async def event_handler(event_data):
            received_events.append(event_data)
        
        consumer = KafkaEventConsumer(event_handler)
        
        # Act - Produce message
        producer.enqueue(test_event)
        
        # Act - Consume message (with timeout)
        import threading
        import time
        
        def consume_with_timeout():
            consumer.consumer.subscribe([kafka_config['topic']])
            start_time = time.time()
            
            while time.time() - start_time < 10:  # 10 second timeout
                msg = consumer.consumer.poll(1.0)
                if msg is not None and not msg.error():
                    event_data = json.loads(msg.value().decode('utf-8'))
                    asyncio.run(event_handler(event_data))
                    break
            
            consumer.consumer.close()
        
        consumer_thread = threading.Thread(target=consume_with_timeout)
        consumer_thread.start()
        consumer_thread.join()
        
        # Assert
        assert len(received_events) == 1
        assert received_events[0]["type"] == "test_event"
        assert received_events[0]["user_id"] == "test_user"
```

---

## End-to-End Tests

### Full Workflow Tests

```python
# tests/e2e/test_workflows.py
import pytest
import httpx
import asyncio
import time
from uuid import uuid4

class TestE2EWorkflows:
    @pytest.fixture
    def publisher_client(self):
        return httpx.AsyncClient(base_url="http://localhost:8000")
    
    @pytest.fixture
    def subscriber_client(self):
        return httpx.AsyncClient(base_url="http://localhost:8001")
    
    @pytest.mark.asyncio
    async def test_user_analytics_end_to_end(self, publisher_client, subscriber_client):
        """Test complete user analytics workflow"""
        # Arrange
        user_id = f"test_user_{uuid4().hex[:8]}"
        event_data = {
            "user_id": user_id,
            "event_type": "page_view",
            "timestamp": "2024-01-01T12:00:00Z",
            "metadata": {"page": "/test", "source": "e2e_test"}
        }
        
        # Act - Publish event
        response = await publisher_client.post(
            "/api/v1/events/analytics",
            json=event_data
        )
        
        # Assert - Event published successfully
        assert response.status_code == 202
        assert response.json()["message"] == "Event published"
        
        # Wait for processing
        await asyncio.sleep(3)
        
        # Act - Retrieve processed event
        response = await subscriber_client.get(f"/api/v1/events/user/{user_id}")
        
        # Assert - Event was processed and stored
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert len(data["events"]) >= 1
        
        # Find our event
        our_event = next(
            (e for e in data["events"] if e["event_type"] == "page_view"),
            None
        )
        assert our_event is not None
        assert our_event["metadata"]["page"] == "/test"
    
    @pytest.mark.asyncio
    async def test_chemical_research_end_to_end(self, publisher_client, subscriber_client):
        """Test complete chemical research workflow with LLM processing"""
        # Arrange
        molecule_id = f"mol_test_{uuid4().hex[:8]}"
        researcher = f"Dr. Test_{uuid4().hex[:8]}"
        event_data = {
            "molecule_id": molecule_id,
            "researcher": researcher,
            "data": {
                "formula": "H2O",
                "weight": 18.015,
                "state": "liquid"
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        # Act - Publish event
        response = await publisher_client.post(
            "/api/v1/events/chemical",
            json=event_data
        )
        
        # Assert - Event published successfully
        assert response.status_code == 202
        
        # Wait for LLM processing
        await asyncio.sleep(5)
        
        # Act - Retrieve processed event
        response = await subscriber_client.get(
            f"/api/v1/events/researcher/{researcher.replace(' ', '%20')}"
        )
        
        # Assert - Event was processed with LLM properties
        assert response.status_code == 200
        data = response.json()
        assert data["researcher"] == researcher
        assert len(data["events"]) >= 1
        
        # Find our event
        our_event = next(
            (e for e in data["events"] if e["molecule_id"] == molecule_id),
            None
        )
        assert our_event is not None
        assert our_event["data"]["formula"] == "H2O"
        assert "llm_properties" in our_event
        assert our_event["llm_properties"]["color"] == "colorless"
        assert our_event["llm_properties"]["ph"] == 7.0
```

---

## Performance Tests

### Load Testing

```python
# tests/performance/test_load.py
import pytest
import httpx
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import statistics

class TestPerformance:
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_publisher_concurrent_load(self):
        """Test publisher service under concurrent load"""
        client = httpx.AsyncClient(base_url="http://localhost:8000")
        
        async def send_request(request_id):
            event_data = {
                "user_id": f"load_test_user_{request_id}",
                "event_type": "load_test",
                "timestamp": "2024-01-01T12:00:00Z",
                "metadata": {"request_id": request_id}
            }
            
            start_time = time.time()
            response = await client.post("/api/v1/events/analytics", json=event_data)
            end_time = time.time()
            
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "request_id": request_id
            }
        
        # Send 100 concurrent requests
        tasks = [send_request(i) for i in range(100)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        response_times = [r["response_time"] for r in results]
        success_count = sum(1 for r in results if r["status_code"] == 202)
        
        # Assertions
        assert success_count >= 95  # At least 95% success rate
        assert statistics.mean(response_times) < 1.0  # Average response time < 1s
        assert max(response_times) < 5.0  # Max response time < 5s
        
        print(f"Load test results:")
        print(f"- Total requests: 100")
        print(f"- Successful requests: {success_count}")
        print(f"- Average response time: {statistics.mean(response_times):.3f}s")
        print(f"- Max response time: {max(response_times):.3f}s")
        print(f"- Min response time: {min(response_times):.3f}s")
    
    @pytest.mark.performance
    def test_database_bulk_operations(self):
        """Test database performance with bulk operations"""
        # This would test database performance under load
        pass
```

### Stress Testing

```python
# tests/performance/test_stress.py
import pytest
import httpx
import asyncio
import psutil
import time

class TestStress:
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Monitor memory usage during high load"""
        client = httpx.AsyncClient(base_url="http://localhost:8000")
        
        # Monitor system resources
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        async def stress_request(request_id):
            # Create large payload to stress memory
            large_metadata = {f"key_{i}": f"value_{i}" * 100 for i in range(50)}
            
            event_data = {
                "user_id": f"stress_user_{request_id}",
                "event_type": "stress_test",
                "timestamp": "2024-01-01T12:00:00Z",
                "metadata": large_metadata
            }
            
            response = await client.post("/api/v1/events/analytics", json=event_data)
            return response.status_code == 202
        
        # Send many requests rapidly
        tasks = [stress_request(i) for i in range(500)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Assertions
        success_count = sum(1 for r in results if r is True)
        assert success_count >= 400  # At least 80% success under stress
        assert memory_increase < 500  # Memory increase < 500MB
        
        print(f"Stress test results:")
        print(f"- Initial memory: {initial_memory:.2f} MB")
        print(f"- Final memory: {final_memory:.2f} MB")
        print(f"- Memory increase: {memory_increase:.2f} MB")
        print(f"- Successful requests: {success_count}/500")
```

---

## Test Configuration

### pytest.ini

```ini
[tool:pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    stress: Stress tests
    slow: Slow running tests

testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*

addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes

asyncio_mode = auto
```

### Test Environment Configuration

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  test-kafka:
    image: confluentinc/cp-kafka:7.4.0
    environment:
      KAFKA_ZOOKEEPER_CONNECT: test-zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports:
      - "9092:9092"
    depends_on:
      - test-zookeeper

  test-zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  test-postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: test_events_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5433:5432"

  test-redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: password
          POSTGRES_DB: test_events_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r event_publisher_service/requirements.txt
        pip install -r event_subscriber_service/requirements.txt
    
    - name: Start Kafka
      run: |
        docker run -d --name zookeeper -p 2181:2181 confluentinc/cp-zookeeper:7.4.0
        docker run -d --name kafka -p 9092:9092 --link zookeeper confluentinc/cp-kafka:7.4.0
    
    - name: Run Publisher Tests
      run: |
        cd event_publisher_service
        pytest --cov=app --cov-report=xml
    
    - name: Run Subscriber Tests
      run: |
        cd event_subscriber_service
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

This comprehensive testing guide ensures high code quality, reliability, and performance of the Event-Driven Platform through thorough testing at all levels.
