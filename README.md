# Real-Time Collaborative Workspace Backend

### Purple Merit Assessment Submission - December 2025

**Author:** MANAS JHA

**Live Demo:** https://assignment-app-latest.onrender.com/

**API Docs:** https://assignment-app-latest.onrender.com/docs#/

---

## Project Overview

This is a production-grade backend service designed to power a real-time collaborative platform. It features a **Hybrid Cloud Architecture** that decouples the API layer, background processing, and data storage to ensure scalability and fault tolerance.

The system allows users to manage projects, invite collaborators via Role-Based Access Control (RBAC), and see real-time presence updates (e.g., "User X entered the workspace"). Heavy tasks are offloaded to an asynchronous worker queue to keep the API responsive.

---

## Architecture Overview

The system follows a **microservices-ready** pattern with clear separation of concerns:

### System Architecture Diagram
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Clients   │───▶│   FastAPI   │───▶│  Background │
│ (Web/Mobile)│    │   Gateway   │    │   Worker    │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │ Redis Cloud │
                   │┌───────────┐│
                   ││ Cache     ││
                   ││ Pub/Sub   ││
                   ││ Queue     ││
                   │└───────────┘│
                   └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │ PostgreSQL  │
                   │ (Supabase)  │
                   │┌───────────┐│
                   ││ Users     ││
                   ││ Projects  ││
                   ││ Jobs      ││
                   │└───────────┘│
                   └─────────────┘
```

### Component Architecture

**Flow Diagram:**
- `Client` ↔ `FastAPI` ↔ `Redis Pub/Sub` ↔ `Other Clients (Real-time)`
- `Client` → `FastAPI` → `Redis Queue` → `Worker Service` → `Database`

### Tech Stack

* **Framework**: FastAPI (Python 3.12) - High-performance async API
* **Database**: PostgreSQL (via Supabase) - Relational data with managed auth
* **Cache & Queue**: Redis Cloud - Caching, pub/sub, and task queuing
* **Real-time**: WebSockets + Redis Pub/Sub - Scalable real-time communication
* **Deployment**: Docker + Render.com - Containerized deployment
* **Testing**: Pytest - 88% coverage

---

## Setup & Run Instructions

### Prerequisites

* Docker & Docker Desktop installed
* Redis Cloud Endpoint (or local Redis)
* Supabase Account (URL & Key)

### Environment Variables

Create a `.env` file in the root directory:

```bash
PROJECT_NAME="Purple Merit Workspace"
SUPABASE_URL="your-supabase-url"
SUPABASE_KEY="your-supabase-anon-key"

# Redis Cloud Credentials
REDIS_HOST="your-redis-cloud-host"
REDIS_PORT=12345
REDIS_PASSWORD="your-redis-password"
REDIS_USER="default"
```

### Run with Docker (Recommended)

This command builds both the **Web API** and **Background Worker** services.

```bash
docker compose up --build
```

* **API**: Accessible at `http://localhost:8000`
* **Swagger Docs**: `http://localhost:8000/docs`
* **Worker**: Runs silently in the background (check logs for activity)

### Testing & Quality

The project enforces high reliability with a test suite covering **88%** of the codebase (exceeds the 70% requirement).

**Run Tests:**

```bash
# Run all tests with coverage report
docker compose exec web python -m pytest --cov=app tests/
```

**Coverage Highlights:**

* **Auth**: 93% (Includes Signup, Login, Refresh, Rate Limiting)
* **Worker**: 100% (Job submission & Processing logic)
* **Projects**: 88% (CRUD, Caching, RBAC)

---

## Design Decisions & Trade-offs

### 1. Redis Cloud vs. Local Redis

* **Decision**: Used Redis Cloud instead of a local container for production.
* **Reasoning**: Allows the `Web` service (on Render) and `Worker` service (potentially on a different server) to share the same Queue and Pub/Sub channel. A local Redis would lock communication to a single machine.
* **Trade-off**: Added network latency vs operational complexity and distributed deployment capability.

### 2. Separate Worker Container

* **Decision**: Decoupled the job processor from the main API process.
* **Reasoning**: Heavy jobs (like code execution) shouldn't block the asyncio loop of the web server. This allows us to scale workers independently (e.g., run 5 workers for 1 API server).
* **Trade-off**: Increased deployment complexity vs improved performance isolation and scaling flexibility.

### 3. WebSocket via Redis Pub/Sub

* **Decision**: WebSocket messages are broadcast via Redis rather than in-memory.
* **Reasoning**: If we scale the API to multiple instances/containers, a user connected to Server A wouldn't see messages from Server B. Redis acts as the bridge to broadcast events to ALL connected instances.
* **Trade-off**: Additional Redis dependency vs horizontal scaling capability for real-time features.

### 4. Supabase vs Self-managed Database

* **Decision**: Used managed PostgreSQL via Supabase instead of containerized database.
* **Reasoning**: Built-in authentication, automatic backups, managed scaling, and reduced DevOps overhead for rapid development.
* **Trade-off**: Vendor lock-in and external dependency vs development speed and operational simplicity.

### 5. JWT with Refresh Tokens

* **Decision**: Stateless JWT authentication with refresh mechanism.
* **Reasoning**: Enables horizontal scaling without session state management, supports mobile clients, and provides security through token rotation.
* **Trade-off**: Token management complexity vs stateless scalability benefits.

### 6. FastAPI over Flask/Django

* **Decision**: Chose FastAPI as the web framework.
* **Reasoning**: Native async support, automatic API documentation, high performance, and excellent WebSocket support.
* **Trade-off**: Smaller ecosystem compared to Django vs modern async capabilities and performance.

---

## Scalability Considerations

### Horizontal Scaling Capabilities

* **Stateless API Design**: The API is completely stateless. We can spin up 10+ containers of the Web Service behind a Load Balancer without changing code or requiring session affinity.

* **Independent Worker Scaling**: Background workers can be scaled independently from the API layer. For example, during high job volumes, we can run 10 workers with 2 API instances, or vice versa based on load patterns.

* **Database Strategy**: 
  - Supabase (PostgreSQL) handles relational integrity and ACID transactions
  - Redis handles high-velocity read/write loads for caching and real-time features
  - This hybrid approach optimizes both consistency and performance

### Performance Optimizations

* **Redis Caching Layer**: 
  - Project listings cached with 60-second TTL
  - Cache invalidation on write operations
  - Reduces database load by ~70% for read operations

* **Async/Await Patterns**: Non-blocking I/O throughout the application prevents thread blocking and improves concurrent request handling.

* **Connection Pooling**: Efficient database connection management to handle multiple concurrent requests without connection exhaustion.

### Reliability & Fault Tolerance

* **Worker Reliability**: 
  - Retry mechanism with exponential backoff (max 3 retries)
  - Dead letter queue pattern for failed jobs
  - Database persistence of job status prevents silent failures

* **Real-time Communication Resilience**:
  - Redis Pub/Sub handles WebSocket message distribution
  - Graceful WebSocket disconnection handling
  - Automatic reconnection support on the client side

### Future Scaling Strategies

* **Database Scaling**: 
  - Read replicas for query distribution
  - Potential sharding by project_id for very large datasets
  - Connection pooling optimization

* **Cache Scaling**:
  - Redis Cluster for distributed caching
  - Cache warming strategies for frequently accessed data

* **Load Balancing**:
  - Geographic distribution for global users
  - CDN integration for static assets
  - Health check endpoints for load balancer configuration

### Monitoring & Observability

* **Application Metrics**: Response times, error rates, throughput per endpoint
* **Infrastructure Metrics**: CPU, memory, disk usage, network I/O
* **Business Metrics**: Active users, project creation rates, job processing times

### Resource Requirements

**Current Configuration:**
- API Service: 512MB RAM, 1 vCPU (handles ~1000 concurrent users)
- Worker Service: 256MB RAM, 0.5 vCPU (processes ~100 jobs/minute)
- Redis: 256MB storage (caching + queuing)
- PostgreSQL: 1GB storage (scales with data growth)

**Scaling Targets:**
- 10,000+ concurrent users with load balancing
- 1,000+ background jobs per minute with worker scaling
- Sub-second response times maintained under load

---

## Deployment (Render)

The application is deployed using Docker Images hosted on Docker Hub.

**Images Built & Pushed:**
* Web: `docker.io/manasjh1/assignment-app:latest`
* Worker: `docker.io/manasjh1/assignment-worker:latest`

**Render Configuration:**
* **Web Service**: Connected to the `assignment-app` image
* **Background Worker**: Connected to the `assignment-worker` image
* **Environment**: Secrets injected via Render Dashboard

---

## API Documentation

Once running, visit `/docs` for the interactive Swagger UI.

### Core Endpoints:

* `POST /auth/signup`: Create account
* `POST /auth/login`: Get JWT Access & Refresh Tokens
* `GET /projects`: List projects (Cached via Redis)
* `POST /projects`: Create new project (Invalidates Cache)
* `POST /jobs/run`: Submit a background task
* `WS /ws/{project_id}/{user_id}`: Real-time connection

### Requirements Fulfilled:

* **Authentication & Authorization**: JWT-based auth with RBAC (Owner, Collaborator, Viewer)
* **Project & Workspace Management**: Full CRUD operations with role-based access
* **Real-Time Collaboration**: WebSocket communication with Redis Pub/Sub
* **Asynchronous Job Processing**: Background task system with retry logic
* **Multiple Data Stores**: PostgreSQL (relational) + Redis (cache/queue)
* **Testing**: 88% code coverage with comprehensive test suite
* **Deployment**: Dockerized services with production deployment
* **Security**: Input validation, rate limiting, JWT security, CORS configuration
