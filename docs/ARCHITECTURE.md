# Architecture Documentation

## System Overview

The Event-Driven Microservices Platform is designed using **Hexagonal Architecture** (Ports and Adapters) principles, ensuring clean separation of concerns and high testability. The platform consists of two main microservices that communicate asynchronously through Apache Kafka.

## Architecture Patterns Implemented

### 1. Hexagonal Architecture (Ports and Adapters)
- **Core Domain**: Business logic is isolated in the `core` modules
- **Ports**: Abstract interfaces define contracts (e.g., `DatabaseRepository`, `LLMService`)
- **Adapters**: Concrete implementations of ports (e.g., `PostgreSQLRepository`, `MockLLMService`)
- **API Layer**: External interfaces for the system

### 2. Repository Pattern
- Abstract database operations through interfaces
- Easy to test with mock implementations
- Database technology can be swapped without changing business logic

### 3. Factory Pattern
- Service creation and dependency injection
- Configuration-based service instantiation
- Support for different implementations (mock vs real services)

### 4. Event-Driven Architecture
- Asynchronous communication through Kafka
- Loose coupling between services
- Scalable event processing

## Service Architecture

### Event Publisher Service

```
┌─────────────────────────────────────────────────────────────┐
│                    Event Publisher Service                   │
├─────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                        │
│  ├── models.py (Pydantic models)                           │
│  ├── routes.py (REST endpoints)                            │
│  └── transformers.py (Data transformation)                 │
├─────────────────────────────────────────────────────────────┤
│  Core Layer                                                 │
│  └── event_service.py (Business logic)                     │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                       │
│  ├── event_queue.py (Abstract interface)                   │
│  └── kafka_producer.py (Kafka implementation)              │
├─────────────────────────────────────────────────────────────┤
│  Configuration                                              │
│  └── settings.py (Environment-based config)                │
└─────────────────────────────────────────────────────────────┘
```

### Event Subscriber Service

```
┌─────────────────────────────────────────────────────────────┐
│                   Event Subscriber Service                  │
├─────────────────────────────────────────────────────────────┤
│  API Worker Layer (Celery)                                 │
│  └── handlers.py (Event type routing & task management)    │
├─────────────────────────────────────────────────────────────┤
│  Core Layer                                                 │
│  ├── event_processing_service.py (Business logic)          │
│  └── data_analytics_service.py (Analytics functions)       │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                       │
│  ├── kafka_consumer.py (Kafka message consumption)         │
│  ├── database_repository.py (Abstract interface)           │
│  ├── postgresql_repository.py (PostgreSQL implementation)  │
│  ├── llm_service.py (LLM integration)                      │
│  └── database_models.py (SQLAlchemy models)                │
├─────────────────────────────────────────────────────────────┤
│  Main Worker                                                │
│  ├── main_worker.py (Kafka consumer coordination)          │
│  └── main.py (Monitoring API)                              │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

```
[Client] → [Publisher API] → [Kafka] → [Subscriber Worker] → [PostgreSQL]
                                              ↓
                                         [LLM Service]
                                              ↓
                                         [Celery Tasks]
```

### Detailed Flow:

1. **Event Ingestion**: Client sends HTTP POST to Publisher Service
2. **Event Transformation**: API layer validates and transforms data
3. **Event Publishing**: Core service publishes to Kafka topic
4. **Event Consumption**: Subscriber service consumes from Kafka
5. **Task Dispatch**: Events are dispatched to appropriate Celery tasks
6. **Processing**: Business logic processes events (including LLM calls)
7. **Persistence**: Processed data is stored in PostgreSQL
8. **Analytics**: Real-time analytics available through Subscriber API

## Technology Stack & Justification

### Core Technologies

| Technology | Purpose | Justification |
|------------|---------|---------------|
| **Python 3.8+** | Primary language | Rich ecosystem, excellent async support |
| **FastAPI** | Web framework | High performance, automatic OpenAPI docs, type hints |
| **Apache Kafka** | Message broker | High throughput, fault tolerance, message ordering |
| **PostgreSQL** | Primary database | ACID compliance, JSON support, mature ecosystem |
| **Celery** | Task queue | Distributed task processing, retry mechanisms |
| **Redis** | Celery broker | In-memory performance, pub/sub capabilities |
| **SQLAlchemy** | ORM | Database abstraction, migration support |
| **Pydantic** | Data validation | Type safety, automatic validation, serialization |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Container Runtime** | Docker | Consistent environments, easy deployment |
| **Orchestration** | Docker Compose | Local development, service coordination |
| **Process Management** | Uvicorn, Celery | ASGI server, distributed task processing |
| **Monitoring** | Built-in endpoints | Health checks, metrics, analytics |

## Scalability Considerations

### Horizontal Scaling

1. **Publisher Service**: Multiple instances behind load balancer
2. **Subscriber Service**: Multiple Kafka consumer groups
3. **Celery Workers**: Scale worker processes based on queue depth
4. **Database**: Read replicas, connection pooling

### Performance Optimizations

1. **Kafka Configuration**:
   - Batch processing for higher throughput
   - Compression (gzip) for reduced network overhead
   - Partitioning for parallel processing

2. **Database Optimization**:
   - Indexed columns for frequent queries
   - JSONB for flexible metadata storage
   - Connection pooling for reduced overhead

3. **Async Processing**:
   - Non-blocking I/O throughout the stack
   - Background task processing with Celery
   - Async database operations

## Fault Tolerance & Reliability

### Error Handling Strategies

1. **Retry Mechanisms**:
   - Kafka producer retries with exponential backoff
   - Celery task retries with configurable policies
   - Database operation retries with circuit breaker pattern

2. **Dead Letter Queues**:
   - Failed messages routed to DLQ for manual inspection
   - Poison message detection and isolation
   - Failed task tracking in database

3. **Graceful Degradation**:
   - LLM service fallback to mock implementation
   - Service health checks and monitoring
   - Partial failure handling

### Data Consistency

1. **Event Ordering**: Kafka partition keys ensure related events are processed in order
2. **Idempotency**: Event processing is idempotent using unique event IDs
3. **Transaction Management**: Database operations wrapped in transactions
4. **Audit Trail**: All events tracked with processing status

## Security Considerations

### Authentication & Authorization
- API key authentication for LLM services
- Service-to-service authentication planned
- Input validation and sanitization

### Data Protection
- Sensitive data encryption at rest (PostgreSQL)
- TLS for service communication
- Input validation preventing injection attacks

### Network Security
- Internal service communication over private networks
- Firewall rules restricting external access
- API rate limiting and throttling

## Monitoring & Observability

### Health Checks
- Service health endpoints (`/healthz`)
- Infrastructure dependency checks
- Automated health monitoring

### Metrics & Analytics
- Service-level metrics (`/metrics`)
- Business metrics (event processing rates)
- Real-time analytics through Subscriber API

### Logging
- Structured logging with correlation IDs
- Centralized log aggregation capability
- Error tracking and alerting

## Deployment Architecture

### Local Development
```
Docker Compose
├── Kafka + Zookeeper
├── PostgreSQL
├── Redis
└── Kafka UI (monitoring)
```

### Production Considerations
- Kubernetes deployment manifests
- Multi-zone deployment for high availability
- External managed services (AWS MSK, RDS, ElastiCache)
- Auto-scaling based on metrics

## Testing Strategy

### Test Pyramid

1. **Unit Tests** (70%):
   - Core business logic testing
   - Mock dependencies for isolation
   - Fast execution, comprehensive coverage

2. **Integration Tests** (20%):
   - Database integration testing
   - Kafka message flow testing
   - Service interaction testing

3. **End-to-End Tests** (10%):
   - Full workflow testing
   - Performance testing
   - Chaos engineering tests

### Test Infrastructure
- Pytest framework with async support
- Test containers for integration tests
- Mock services for external dependencies
- Continuous integration pipeline

## Future Enhancements

### Short Term
- Service mesh implementation (Istio)
- Enhanced monitoring (Prometheus + Grafana)
- API versioning strategy
- Enhanced security (OAuth2, JWT)

### Long Term
- Multi-region deployment
- Event sourcing implementation
- Machine learning pipeline integration
- Real-time stream processing (Kafka Streams)

This architecture provides a solid foundation for a scalable, maintainable, and robust event-driven platform that can handle high-volume concurrent requests while maintaining data consistency and fault tolerance.
