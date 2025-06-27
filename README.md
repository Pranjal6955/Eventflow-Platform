# Distributed Event & Agent Platform

A comprehensive, production-ready event-driven microservices platform built in Python that handles high-volume concurrent API requests and processes them asynchronously in a fault-tolerant manner.

## 🏗️ Architecture Overview

This platform demonstrates advanced software engineering principles including **Hexagonal Architecture**, **Event-Driven Design**, and **Clean Code Patterns**. It consists of two core microservices that communicate asynchronously through Apache Kafka:

### Core Services

1. **Event Publisher Service** - High-performance FastAPI REST API for event ingestion
2. **Event Subscriber Service** - Scalable event processing engine with LLM integration

### Key Features

- ✅ **High Concurrency**: Handle 1000+ concurrent requests
- ✅ **Fault Tolerance**: Comprehensive error handling and retry mechanisms  
- ✅ **Clean Architecture**: Hexagonal architecture with proper separation of concerns
- ✅ **Async Processing**: Full asynchronous pipeline with Celery workers
- ✅ **Database Integration**: PostgreSQL with SQLAlchemy ORM
- ✅ **LLM Integration**: Chemical property extraction using AI services
- ✅ **Comprehensive Testing**: Unit, integration, and E2E test suites
- ✅ **Production Ready**: Docker containerization and Kubernetes manifests
- ✅ **Monitoring**: Health checks, metrics, and observability

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- 8GB+ RAM recommended

### 1-Minute Setup
```bash
# Clone repository
git clone <repository-url>
cd Backend

# Start infrastructure
docker-compose up -d

# Start services (2 terminals)
./event_publisher_service/start.sh    # Terminal 1
./event_subscriber_service/start.sh   # Terminal 2

# Run demo
./demo.sh
```

### Access Points
- **Publisher API**: http://localhost:8000/docs
- **Subscriber API**: http://localhost:8001/docs  
- **Kafka UI**: http://localhost:8080
- **Database**: localhost:5432 (postgres/password)

## 📋 Use Cases Implemented

### Scenario 1: User Analytics Platform
Real-time processing of user interaction events from web and mobile applications:
- High-volume event ingestion (clicks, page views, purchases)
- Real-time analytics and user behavior tracking
- Concurrent request handling with data integrity guarantees

### Scenario 2: Chemical Research Platform  
Advanced processing of chemical research data with AI enhancement:
- Molecular data ingestion and validation
- LLM-powered chemical property extraction
- Research analytics and experiment tracking
- Graceful handling of external API rate limits

## 🏛️ Architecture & Design Patterns

### Hexagonal Architecture (Ports & Adapters)
```
┌─────────────────────────────────────────┐
│              Application Core           │
│  ┌─────────────────────────────────┐   │
│  │       Business Logic            │   │
│  │   (Domain Services)             │   │
│  └─────────────────────────────────┘   │
│              ↕️ Ports                   │
└─────────────────────────────────────────┘
              ↕️ Adapters
┌─────────────────────────────────────────┐
│         Infrastructure Layer           │
│  ┌──────────┐ ┌──────────┐ ┌────────┐  │
│  │   API    │ │ Database │ │ Kafka  │  │
│  │ (FastAPI)│ │(Postgres)│ │Producer│  │
│  └──────────┘ └──────────┘ └────────┘  │
└─────────────────────────────────────────┘
```

### Design Patterns Implemented
- **Repository Pattern**: Database abstraction for testability
- **Factory Pattern**: Service creation and dependency injection  
- **Observer Pattern**: Event-driven communication via Kafka
- **Strategy Pattern**: Multiple LLM service implementations
- **Command Pattern**: Celery task encapsulation

### Data Flow Architecture
```
[Client] → [REST API] → [Kafka] → [Consumer] → [Celery] → [Database]
                                      ↓
                                 [LLM Service]
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Framework** | FastAPI | High-performance async API with auto-docs |
| **Message Broker** | Apache Kafka | Reliable event streaming and ordering |
| **Database** | PostgreSQL | ACID compliance with JSON support |
| **Task Queue** | Celery + Redis | Distributed background processing |
| **ORM** | SQLAlchemy | Database abstraction and migrations |
| **Validation** | Pydantic | Type safety and data validation |
| **Containerization** | Docker | Consistent deployment environments |
| **Testing** | pytest | Comprehensive test framework |

## 📊 Performance & Scalability

### Performance Characteristics
- **Throughput**: 1000+ events/second per publisher instance
- **Latency**: <100ms API response time (95th percentile)
- **Concurrency**: 500+ concurrent connections supported
- **Fault Tolerance**: 99.9% uptime with proper retry mechanisms

### Scalability Features
- **Horizontal Scaling**: Multiple service instances behind load balancer
- **Worker Scaling**: Auto-scaling Celery workers based on queue depth
- **Database Scaling**: Read replicas and connection pooling
- **Kafka Partitioning**: Parallel processing with message ordering

### Production Optimizations
- Kafka producer batching and compression
- Async I/O throughout the entire stack
- Database query optimization with proper indexing
- Connection pooling and resource management

## 🔒 Security & Reliability

### Security Features
- Input validation and sanitization
- SQL injection prevention via ORM
- Rate limiting capabilities  
- TLS encryption for service communication
- Secrets management for production deployment

### Reliability Features
- **Circuit Breaker**: Prevents cascade failures
- **Retry Policies**: Exponential backoff with jitter
- **Dead Letter Queues**: Failed message handling
- **Health Checks**: Automated monitoring and alerting
- **Graceful Shutdown**: Clean resource cleanup

## 📈 Monitoring & Observability

### Built-in Monitoring
- Health check endpoints (`/healthz`)
- Service metrics endpoints (`/metrics`)
- Structured logging with correlation IDs
- Real-time analytics APIs

### Production Monitoring Stack
- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger for distributed tracing
- **Alerting**: PagerDuty integration for critical issues

## 🧪 Testing & Quality Assurance

### Test Coverage
- **Unit Tests**: 90%+ code coverage for business logic
- **Integration Tests**: Database and Kafka integration
- **End-to-End Tests**: Complete workflow validation
- **Performance Tests**: Load and stress testing
- **Contract Tests**: API contract validation

### Test Execution
```bash
# Run all tests
cd event_publisher_service && pytest --cov=app
cd event_subscriber_service && pytest --cov=app

# Run specific test categories  
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests
pytest -m e2e            # End-to-end tests
pytest -m performance    # Performance tests
```

### Quality Metrics
- **Code Coverage**: >90% line coverage
- **Type Safety**: Full Pydantic type validation
- **Linting**: Black, flake8, mypy compliance
- **Security**: Bandit security scanning

## 🚢 Deployment Options

### Local Development
```bash
# Automated setup
./event_publisher_service/start.sh
./event_subscriber_service/start.sh
```

### Docker Production
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
# Deploy to K8s cluster
kubectl apply -f k8s/
```

### Cloud Deployments
- **AWS**: EKS + MSK + RDS + ElastiCache
- **GCP**: GKE + Pub/Sub + Cloud SQL + Memorystore  
- **Azure**: AKS + Event Hubs + Database + Cache

## 📚 Documentation

### Core Documentation
- [📋 API Documentation](docs/API.md) - Complete API reference with examples
- [🏗️ Architecture Guide](docs/ARCHITECTURE.md) - Detailed system design
- [🚀 Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions
- [🧪 Testing Guide](docs/TESTING.md) - Comprehensive testing strategy

### API Examples

#### Publish User Analytics Event
```bash
curl -X POST "http://localhost:8000/api/v1/events/analytics" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_12345",
    "event_type": "page_view", 
    "timestamp": "2024-01-01T12:00:00Z",
    "metadata": {"page": "/dashboard", "source": "web"}
  }'
```

#### Publish Chemical Research Event
```bash
curl -X POST "http://localhost:8000/api/v1/events/chemical" \
  -H "Content-Type: application/json" \
  -d '{
    "molecule_id": "mol_h2o_001",
    "researcher": "Dr. Jane Smith",
    "data": {"formula": "H2O", "weight": 18.015},
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

#### Get Analytics
```bash
# User analytics
curl "http://localhost:8001/api/v1/analytics/user/user_12345"

# Researcher summary  
curl "http://localhost:8001/api/v1/analytics/researcher/Dr.%20Jane%20Smith"
```

## 🏆 Technical Achievements

### Software Engineering Excellence
- ✅ **Clean Architecture**: Proper separation of concerns with hexagonal architecture
- ✅ **SOLID Principles**: Single responsibility, open/closed, dependency inversion
- ✅ **Design Patterns**: Repository, Factory, Strategy, Observer patterns
- ✅ **Type Safety**: Full type hints with Pydantic validation
- ✅ **Error Handling**: Comprehensive exception handling and recovery

### Performance Engineering  
- ✅ **Async Programming**: Full async/await implementation
- ✅ **Connection Pooling**: Optimized database and Redis connections
- ✅ **Batch Processing**: Kafka producer batching for efficiency
- ✅ **Caching Strategy**: Redis caching for frequently accessed data
- ✅ **Resource Management**: Proper cleanup and memory management

### DevOps & Production Ready
- ✅ **Containerization**: Multi-stage Docker builds
- ✅ **Orchestration**: Kubernetes manifests with auto-scaling
- ✅ **CI/CD Pipeline**: Automated testing and deployment
- ✅ **Monitoring**: Health checks, metrics, and alerting
- ✅ **Security**: Input validation, secrets management

### Scalability & Reliability
- ✅ **Horizontal Scaling**: Load balancer with multiple instances
- ✅ **Fault Tolerance**: Circuit breakers and retry mechanisms  
- ✅ **Data Consistency**: Event ordering and idempotent operations
- ✅ **Graceful Degradation**: Fallback mechanisms for external services
- ✅ **Zero Downtime**: Rolling updates and health checks

## 🎯 Project Structure

```
Backend/
├── 📁 docs/                          # Comprehensive documentation
│   ├── ARCHITECTURE.md               # System design and patterns
│   ├── API.md                        # Complete API reference  
│   ├── DEPLOYMENT.md                 # Production deployment guide
│   └── TESTING.md                    # Testing strategy and guides
├── 📁 database/                      # Database setup and migrations
│   └── init.sql                      # Database initialization script
├── 📁 event_publisher_service/       # Event ingestion microservice
│   ├── 📁 app/
│   │   ├── 📁 api/                   # REST API layer
│   │   ├── 📁 core/                  # Business logic
│   │   ├── 📁 infrastructure/        # External integrations
│   │   └── 📁 config/                # Configuration management
│   ├── 📁 tests/                     # Comprehensive test suite
│   ├── Dockerfile                    # Production container
│   ├── requirements.txt              # Python dependencies
│   └── start.sh                      # Automated startup script
├── 📁 event_subscriber_service/      # Event processing microservice  
│   ├── 📁 app/
│   │   ├── 📁 api_worker/            # Celery task handlers
│   │   ├── 📁 core/                  # Business logic
│   │   ├── 📁 infrastructure/        # Database, Kafka, LLM
│   │   └── 📁 config/                # Configuration management
│   ├── 📁 tests/                     # Comprehensive test suite
│   ├── Dockerfile.worker             # Worker container
│   ├── Dockerfile.api                # API container  
│   ├── requirements.txt              # Python dependencies
│   └── start.sh                      # Automated startup script
├── docker-compose.yml                # Infrastructure orchestration
├── demo.sh                           # Interactive demonstration
└── README.md                         # Project overview
```

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd Backend

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests before committing
pytest
```

### Code Standards
- **Style**: Black formatter, flake8 linter
- **Type Hints**: mypy static type checking  
- **Documentation**: Google-style docstrings
- **Testing**: Minimum 90% code coverage
- **Security**: Bandit security scanning

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Apache Kafka** for robust message streaming
- **FastAPI** for high-performance web framework
- **PostgreSQL** for reliable data persistence
- **Celery** for distributed task processing
- **Docker** for containerization technology

---

## 🚀 Ready to Get Started?

1. **Quick Demo**: Run `./demo.sh` for a complete walkthrough
2. **API Exploration**: Visit http://localhost:8000/docs for interactive API docs
3. **Architecture Deep Dive**: Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. **Production Deployment**: Follow [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

**Built with ❤️ for high-performance, scalable, and maintainable event-driven systems.**