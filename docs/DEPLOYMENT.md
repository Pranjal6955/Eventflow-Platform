# Deployment Guide

## Overview

This guide covers deployment options for the Event-Driven Microservices Platform, from local development to production environments.

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 10GB free disk space
- **Network**: Internet access for downloading dependencies

### Required Software
- **Docker**: Version 20.10+ and Docker Compose v2
- **Python**: Version 3.8+ (for local development)
- **Git**: For source code management
- **curl/httpie**: For API testing

## Quick Start (Recommended)

### 1. Clone Repository
```bash
git clone <repository-url>
cd Backend
```

### 2. Start Infrastructure
```bash
# Start all infrastructure services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 3. Start Application Services
```bash
# Terminal 1: Start Publisher Service
cd event_publisher_service
./start.sh

# Terminal 2: Start Subscriber Service
cd event_subscriber_service
./start.sh
```

### 4. Run Demo
```bash
# Terminal 3: Run demo script
./demo.sh
```

### 5. Access Services
- **Publisher API**: http://localhost:8000/docs
- **Subscriber API**: http://localhost:8001/docs
- **Kafka UI**: http://localhost:8080
- **Database**: localhost:5432 (postgres/password)

---

## Infrastructure Components

### Docker Compose Services

| Service | Port | Purpose | Dependencies |
|---------|------|---------|--------------|
| **zookeeper** | 2181 | Kafka coordination | None |
| **kafka** | 9092 | Message broker | zookeeper |
| **postgres** | 5432 | Primary database | None |
| **redis** | 6379 | Task queue backend | None |
| **kafka-ui** | 8080 | Kafka monitoring | kafka |

### Service Configuration

#### Kafka Configuration
```yaml
# Key Kafka settings
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
```

#### PostgreSQL Configuration
```yaml
# Database settings
POSTGRES_DB: events_db
POSTGRES_USER: postgres
POSTGRES_PASSWORD: password
```

#### Redis Configuration
```yaml
# Redis settings for Celery
command: redis-server --appendonly yes
```

---

## Local Development Setup

### Option 1: Automated Setup
```bash
# Use provided startup scripts
cd event_publisher_service
./start.sh

cd ../event_subscriber_service
./start.sh
```

### Option 2: Manual Setup

#### Publisher Service
```bash
cd event_publisher_service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start service
python -m app.main
```

#### Subscriber Service
```bash
cd event_subscriber_service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Celery worker (Terminal 1)
celery -A app.api_worker.handlers:app worker --loglevel=info

# Start Kafka consumer (Terminal 2)
python -m app.main_worker

# Start monitoring API (Terminal 3)
python -m app.main
```

---

## Production Deployment

### Docker Production Setup

#### 1. Environment Configuration

Create production environment files:

**`.env.prod.publisher`**:
```env
KAFKA_BOOTSTRAP_SERVERS=kafka-cluster:9092
KAFKA_TOPIC=events_topic_prod
API_PORT=8000
API_BASE_PATH=/api/v1
LOG_LEVEL=INFO
MAX_RETRIES=5
RETRY_DELAY=10
ENABLE_METRICS=true
```

**`.env.prod.subscriber`**:
```env
KAFKA_BOOTSTRAP_SERVERS=kafka-cluster:9092
KAFKA_TOPIC=events_topic_prod
KAFKA_GROUP_ID=event-subscriber-group-prod
POSTGRES_DSN=postgresql://events_user:secure_password@postgres-cluster:5432/events_db_prod
LLM_API_URL=https://api.openai.com/v1
CELERY_BROKER_URL=redis://redis-cluster:6379/0
CELERY_RESULT_BACKEND=redis://redis-cluster:6379/0
API_PORT=8001
LOG_LEVEL=WARNING
MAX_RETRIES=5
RETRY_DELAY=10
```

#### 2. Production Docker Compose

**`docker-compose.prod.yml`**:
```yaml
version: '3.8'

services:
  publisher:
    build:
      context: ./event_publisher_service
      dockerfile: Dockerfile.prod
    env_file:
      - .env.prod.publisher
    ports:
      - "8000:8000"
    depends_on:
      - kafka
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  subscriber-worker:
    build:
      context: ./event_subscriber_service
      dockerfile: Dockerfile.worker.prod
    env_file:
      - .env.prod.subscriber
    depends_on:
      - kafka
      - postgres
      - redis
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  subscriber-api:
    build:
      context: ./event_subscriber_service
      dockerfile: Dockerfile.api.prod
    env_file:
      - .env.prod.subscriber
    ports:
      - "8001:8001"
    depends_on:
      - postgres
    restart: unless-stopped

  # External services would be managed separately
  kafka:
    image: confluentinc/cp-kafka:7.4.0
    # Production Kafka configuration
    
  postgres:
    image: postgres:15-alpine
    # Production PostgreSQL configuration
    
  redis:
    image: redis:7-alpine
    # Production Redis configuration
```

### Kubernetes Deployment

#### 1. Create Kubernetes Manifests

**`k8s/namespace.yaml`**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: event-platform
```

**`k8s/publisher-deployment.yaml`**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: event-publisher
  namespace: event-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: event-publisher
  template:
    metadata:
      labels:
        app: event-publisher
    spec:
      containers:
      - name: publisher
        image: event-publisher:latest
        ports:
        - containerPort: 8000
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "kafka-service:9092"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: event-publisher-service
  namespace: event-platform
spec:
  selector:
    app: event-publisher
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

**`k8s/subscriber-deployment.yaml`**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: event-subscriber-worker
  namespace: event-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: event-subscriber-worker
  template:
    metadata:
      labels:
        app: event-subscriber-worker
    spec:
      containers:
      - name: worker
        image: event-subscriber-worker:latest
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "kafka-service:9092"
        - name: POSTGRES_DSN
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: postgres-dsn
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: event-subscriber-api
  namespace: event-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: event-subscriber-api
  template:
    metadata:
      labels:
        app: event-subscriber-api
    spec:
      containers:
      - name: api
        image: event-subscriber-api:latest
        ports:
        - containerPort: 8001
        env:
        - name: POSTGRES_DSN
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: postgres-dsn
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: event-subscriber-api-service
  namespace: event-platform
spec:
  selector:
    app: event-subscriber-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8001
  type: LoadBalancer
```

#### 2. Deploy to Kubernetes
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy secrets
kubectl create secret generic database-secret \
  --from-literal=postgres-dsn="postgresql://user:pass@postgres:5432/events_db" \
  --namespace=event-platform

# Deploy applications
kubectl apply -f k8s/publisher-deployment.yaml
kubectl apply -f k8s/subscriber-deployment.yaml

# Verify deployment
kubectl get pods -n event-platform
kubectl get services -n event-platform
```

### Cloud Provider Deployments

#### AWS Deployment
```bash
# Using AWS services
# - Amazon MSK (Kafka)
# - Amazon RDS (PostgreSQL)
# - Amazon ElastiCache (Redis)
# - Amazon EKS (Kubernetes)
# - Application Load Balancer

# Example Terraform configuration
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_msk_cluster" "event_platform" {
  cluster_name           = "event-platform-kafka"
  kafka_version          = "3.4.0"
  number_of_broker_nodes = 3

  broker_node_group_info {
    instance_type   = "kafka.m5.large"
    client_subnets  = var.private_subnet_ids
    storage_info {
      ebs_storage_info {
        volume_size = 100
      }
    }
  }
}

resource "aws_rds_instance" "event_platform" {
  identifier     = "event-platform-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  allocated_storage = 20

  db_name  = "events_db"
  username = "postgres"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  skip_final_snapshot = true
}
```

#### Google Cloud Platform
```bash
# Using GCP services
# - Cloud Pub/Sub or Confluent Kafka
# - Cloud SQL (PostgreSQL)
# - Cloud Memorystore (Redis)
# - Google Kubernetes Engine

gcloud container clusters create event-platform \
  --num-nodes=3 \
  --zone=us-central1-a

kubectl apply -f k8s/
```

#### Azure Deployment
```bash
# Using Azure services
# - Azure Event Hubs (Kafka-compatible)
# - Azure Database for PostgreSQL
# - Azure Cache for Redis
# - Azure Kubernetes Service

az aks create \
  --resource-group event-platform-rg \
  --name event-platform-aks \
  --node-count 3 \
  --enable-addons monitoring

kubectl apply -f k8s/
```

---

## Monitoring and Observability

### Health Checks
```bash
# Check service health
curl http://localhost:8000/healthz
curl http://localhost:8001/healthz

# Check infrastructure
curl http://localhost:8080  # Kafka UI
```

### Metrics Collection
```yaml
# Prometheus configuration
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'event-publisher'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics

  - job_name: 'event-subscriber'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: /metrics
```

### Log Aggregation
```yaml
# Fluentd configuration for log collection
<source>
  @type tail
  path /var/log/event-platform/*.log
  pos_file /var/log/fluentd/event-platform.log.pos
  tag event-platform
  format json
</source>

<match event-platform.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name event-platform
</match>
```

---

## Security Considerations

### Production Security Checklist

#### Network Security
- [ ] Configure firewall rules
- [ ] Use private networks for service communication
- [ ] Enable TLS/SSL for all endpoints
- [ ] Implement API gateway with rate limiting

#### Authentication & Authorization
- [ ] Implement API key authentication
- [ ] Set up service-to-service authentication
- [ ] Configure RBAC for Kubernetes
- [ ] Rotate secrets regularly

#### Data Security
- [ ] Enable database encryption at rest
- [ ] Configure secure database connections
- [ ] Implement data retention policies
- [ ] Set up backup encryption

#### Application Security
- [ ] Keep dependencies updated
- [ ] Scan container images for vulnerabilities
- [ ] Implement input validation
- [ ] Configure security headers

---

## Scaling Guidelines

### Horizontal Scaling

#### Publisher Service
```bash
# Scale publisher replicas
kubectl scale deployment event-publisher --replicas=5 -n event-platform

# Auto-scaling based on CPU
kubectl autoscale deployment event-publisher \
  --cpu-percent=70 \
  --min=3 \
  --max=10 \
  -n event-platform
```

#### Subscriber Service
```bash
# Scale worker replicas
kubectl scale deployment event-subscriber-worker --replicas=4 -n event-platform

# Scale based on queue depth
kubectl autoscale deployment event-subscriber-worker \
  --cpu-percent=80 \
  --min=2 \
  --max=8 \
  -n event-platform
```

### Vertical Scaling
```yaml
# Increase resource limits
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

### Database Scaling
```sql
-- Create read replicas for analytics queries
-- Implement connection pooling
-- Use database sharding for high-volume data

-- Connection pooling configuration
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
```

---

## Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check logs
docker-compose logs kafka
docker-compose logs postgres

# Check port conflicts
netstat -tlnp | grep :9092
netstat -tlnp | grep :5432
```

#### Kafka Connection Issues
```bash
# Test Kafka connectivity
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Create test topic
docker exec kafka kafka-topics --create \
  --topic test \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
```

#### Database Connection Issues
```bash
# Test database connection
psql -h localhost -U postgres -d events_db

# Check database logs
docker-compose logs postgres
```

#### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check service metrics
curl http://localhost:8000/metrics
curl http://localhost:8001/metrics

# Monitor Kafka lag
docker exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group event-subscriber-group \
  --describe
```

This deployment guide provides comprehensive instructions for deploying the Event-Driven Platform in various environments, from local development to production cloud deployments.
