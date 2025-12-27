# Real-Time Collaborative Workspace Backend

### Purple Merit Assessment Submission - December 2025

**Author:** [MANAS JHA]

**Live Demo:** [https://assignment-app-latest.onrender.com/]

**API Docs:** [https://assignment-app-latest.onrender.com/docs#/]

---

## 📖 Project Overview

This is a production-grade backend service designed to power a real-time collaborative platform. It features a **Hybrid Cloud Architecture** that decouples the API layer, background processing, and data storage to ensure scalability and fault tolerance.

The system allows users to manage projects, invite collaborators via Role-Based Access Control (RBAC), and see real-time presence updates (e.g., "User X entered the workspace"). Heavy tasks are offloaded to an asynchronous worker queue to keep the API responsive.

---

## 🏗️ Architecture

The system follows a **Microservices-ready** pattern containerized via Docker:

* **API Service (FastAPI)**: Handles REST endpoints, Authentication, and WebSocket connections.
* **Background Worker (Python)**: An independent service that consumes tasks from a Redis Queue for heavy processing (reliability logic included).
* **Data Layer**:
* **PostgreSQL (Supabase)**: Primary relational database for users, projects, and permissions.
* **Redis Cloud**: Used for 1) Caching project data, 2) Pub/Sub for real-time WebSockets, and 3) Task Queueing.



**Flow Diagram:**
`Client` <-> `FastAPI` <-> `Redis Pub/Sub` <-> `Other Clients (Real-time)`
`Client` -> `FastAPI` -> `Redis Queue` -> `Worker Service` -> `Supabase (Result Storage)`

---

## 🛠️ Tech Stack

* **Framework**: FastAPI (Python 3.12)
* **Database**: PostgreSQL (via Supabase)
* **Cache & Queue**: Redis Cloud
* **Real-time**: WebSockets + Redis Pub/Sub
* **Deployment**: Docker, Docker Compose, Render
* **Testing**: Pytest (88% Coverage)

---

## 🚀 Setup & Run Instructions

### 1. Prerequisites

* Docker & Docker Desktop installed.
* Redis Cloud Endpoint (or local Redis).
* Supabase Account (URL & Key).

### 2. Environment Variables

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

### 3. Run with Docker (Recommended)

This command builds both the **Web API** and **Background Worker** services.

```bash
docker compose up --build

```

* **API**: Accessible at `http://localhost:8000`
* **Swagger Docs**: `http://localhost:8000/docs`
* **Worker**: Runs silently in the background (check logs for activity).

---

## ✅ Testing & Quality

The project enforces high reliability with a test suite covering **88%** of the codebase (Exceeds the 70% requirement).

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

## 🚢 Deployment (Render)

The application is deployed using Docker Images hosted on Docker Hub.

1. **Images Built & Pushed**:
* Web: `docker.io/manasjh1/assignment-app:latest`
* Worker: `docker.io/manasjh1/assignment-worker:latest`


2. **Render Configuration**:
* **Web Service**: Connected to the `assignment-app` image.
* **Background Worker**: Connected to the `assignment-worker` image.
* **Environment**: Secrets injected via Render Dashboard.



---

## 💡 Design Decisions & Trade-offs

### 1. Redis Cloud vs. Local Redis

* **Decision**: Used Redis Cloud instead of a local container for production.
* **Reasoning**: Allows the `Web` service (on Render) and `Worker` service (potentially on a different server) to share the same Queue and Pub/Sub channel. A local Redis would lock communication to a single machine.

### 2. Separate Worker Container

* **Decision**: Decoupled the job processor from the main API process.
* **Reasoning**: Heavy jobs (like code execution) shouldn't block the asyncio loop of the web server. This allows us to scale workers independently (e.g., run 5 workers for 1 API server).

### 3. WebSocket via Redis Pub/Sub

* **Decision**: WebSocket messages are broadcast via Redis.
* **Reasoning**: If we scale the API to multiple instances/containers, a user connected to Server A wouldn't see messages from Server B. Redis acts as the bridge to broadcast events to ALL connected instances.

---

## 📈 Scalability Considerations

* **Horizontal Scaling**: The API is stateless. We can spin up 10+ containers of the Web Service behind a Load Balancer without changing code.
* **Database**: Supabase (PostgreSQL) handles relational integrity, while Redis handles high-velocity write/read loads (Caching).
* **Worker Reliability**: The worker implements a "Retry Loop" (Max 3 retries) and updates the database with failure statuses, ensuring no job is silently lost.

---

## 🔗 API Documentation

Once running, visit `/docs` for the interactive Swagger UI.

### Core Endpoints:

* `POST /auth/signup`: Create account.
* `POST /auth/login`: Get JWT Access & Refresh Tokens.
* `GET /projects`: List projects (Cached via Redis).
* `POST /projects`: Create new project (Invalidates Cache).
* `POST /jobs/run`: Submit a background task.
* `WS /ws/{project_id}/{user_id}`: Real-time connection.
