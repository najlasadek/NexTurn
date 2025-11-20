# NexTurn Microservices Architecture

This directory contains the microservices implementation of the NexTurn queue management system.

## Architecture Overview

The application is designed with 8 independent microservices (4 currently implemented):

### ✅ **Implemented Services:**
1. **Frontend Gateway Service** (Port 5000) - Web UI and API Gateway
2. **Authentication Service** (Port 5001) - User authentication and JWT authorization
3. **Business Service** (Port 5002) - Business registration and management
4. **Queue Management Service** (Port 5003) - Queue operations and ticket management

### 🚧 **To Be Implemented:**
5. **Ticket Service** (Port 5004) - Advanced ticket operations and alerts
6. **Feedback Service** (Port 5005) - Customer feedback and ratings
7. **Analytics Service** (Port 5006) - Business analytics and insights
8. **Notification Service** (Port 5007) - Email/SMS/Push notifications

### 🌐 **Infrastructure Services (Planned):**
9. **Message Queue** (RabbitMQ/Kafka) - Asynchronous inter-service communication

## Directory Structure

```
microservices/
├── auth-service/          # Authentication microservice
│   ├── app/              # Application code
│   │   ├── app.py       # Main application
│   │   ├── models.py    # User model
│   │   └── routes.py    # API routes
│   ├── db/              # Database
│   │   └── init_db.py   # Database initialization
│   ├── config/          # Configuration
│   ├── Dockerfile       # Docker configuration
│   └── requirements.txt # Python dependencies
├── business-service/      # Business microservice
│   ├── app/
│   ├── db/
│   ├── config/
│   ├── Dockerfile
│   └── requirements.txt
├── queue-service/         # Queue management microservice
│   ├── app/
│   ├── db/
│   ├── config/
│   ├── Dockerfile
│   └── requirements.txt
├── shared/               # Shared utilities
│   ├── database.py      # Database utilities
│   ├── response.py      # Response formatting
│   └── auth_middleware.py # JWT authentication
├── k8s/                 # Kubernetes manifests
│   ├── namespace.yaml
│   ├── auth-service-deployment.yaml
│   ├── business-service-deployment.yaml
│   ├── queue-service-deployment.yaml
│   └── ingress.yaml
└── docker-compose.yml   # Docker Compose configuration
```

## Prerequisites

### For Docker Deployment:
- Docker Desktop
- Docker Compose

### For Kubernetes Deployment:
- Minikube
- kubectl
- Docker (for building images)

## 🚀 Quick Start - Running with Docker

### **Option 1: Docker Compose (Recommended - Easiest!)**

#### **Step 1: Navigate to microservices directory**
```bash
cd NexTurn/microservices
```

#### **Step 2: Start all services with Docker Compose**
```bash
docker-compose up --build
```

**What happens:**
- 🔨 Builds Docker images for all 4 services
- 🚀 Starts containers in the background
- 🌐 Creates network for service communication
- 💾 Creates volumes for database persistence

**You'll see output like:**
```
✓ Container frontend-service  Started
✓ Container auth-service      Started
✓ Container business-service  Started
✓ Container queue-service     Started

🌐 Frontend Gateway Service started on port 5000
🔐 Authentication Service started on port 5001
🏢 Business Service started on port 5002
📋 Queue Management Service started on port 5003
```

#### **Step 3: Verify services are running**

**Check container status:**
```bash
docker-compose ps
```

**Expected output:**
```
NAME                  STATUS          PORTS
frontend-service      Up 30 seconds   0.0.0.0:5000->5000/tcp
auth-service          Up 30 seconds   0.0.0.0:5001->5001/tcp
business-service      Up 30 seconds   0.0.0.0:5002->5002/tcp
queue-service         Up 30 seconds   0.0.0.0:5003->5003/tcp
```

**Access the application:**
- **Web Interface:** http://localhost:5000
- **Auth API:** http://localhost:5001
- **Business API:** http://localhost:5002
- **Queue API:** http://localhost:5003

**Check service health:**
```bash
# Frontend Gateway
curl http://localhost:5000/health

# Auth Service
curl http://localhost:5001/auth/health

# Business Service
curl http://localhost:5002/api/health

# Queue Service
curl http://localhost:5003/api/health
```

**Expected response for each:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "auth-service"  // or business-service, queue-service
  }
}
```

#### **Step 4: Access services in your browser**
- **Auth Service:** http://localhost:5001
- **Business Service:** http://localhost:5002
- **Queue Service:** http://localhost:5003

#### **Step 5: View logs (optional)**
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f auth-service
docker-compose logs -f business-service
docker-compose logs -f queue-service
```

#### **Step 6: Run automated tests**
```bash
# In a new terminal (while services are running)
./test_services.sh
```

**Expected output:**
```
🧪 NexTurn Microservices Testing Script
========================================
✓ PASSED - User Signup
✓ PASSED - User Login
✓ PASSED - Verify JWT Token
✓ PASSED - Create Business
✓ PASSED - Join Queue
...
Passed: 14
Failed: 0
🎉 All tests passed!
```

#### **Step 7: Stop services**
```bash
# Stop services but keep data
docker-compose stop

# Stop and remove containers (but keep volumes/data)
docker-compose down

# Stop and remove everything including volumes/data
docker-compose down -v
```

---

### **Docker Compose Commands Cheat Sheet**

| Command | Description |
|---------|-------------|
| `docker-compose up` | Start services (use existing images) |
| `docker-compose up --build` | Build images and start services |
| `docker-compose up -d` | Start services in detached mode (background) |
| `docker-compose ps` | List running services |
| `docker-compose logs -f` | Follow logs for all services |
| `docker-compose logs -f auth-service` | Follow logs for specific service |
| `docker-compose stop` | Stop services |
| `docker-compose start` | Start stopped services |
| `docker-compose restart` | Restart services |
| `docker-compose down` | Stop and remove containers |
| `docker-compose down -v` | Stop and remove containers + volumes |
| `docker-compose exec auth-service bash` | Enter service container |

---

### **Troubleshooting Docker**

#### **Problem: Port already in use**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Find what's using the port (e.g., 5001)
# Windows:
netstat -ano | findstr :5001

# Mac/Linux:
lsof -i :5001

# Stop the conflicting process or change ports in docker-compose.yml
```

#### **Problem: Docker daemon not running**
```
Cannot connect to the Docker daemon
```

**Solution:**
- Start Docker Desktop
- Wait for it to fully start (check system tray icon)

#### **Problem: Services can't connect to each other**

**Solution:**
```bash
# Recreate network
docker-compose down
docker-compose up --build
```

#### **Problem: Database not persisting**

**Solution:**
```bash
# Check volumes
docker volume ls

# Recreate with named volumes
docker-compose down -v
docker-compose up --build
```

#### **Problem: Changes not reflecting**

**Solution:**
```bash
# Rebuild images
docker-compose up --build --force-recreate
```

---

### **Complete Test Run Example**

```bash
# 1. Start services
cd NexTurn/microservices
docker-compose up --build -d

# 2. Wait for services to be ready (about 10 seconds)
sleep 10

# 3. Check health
curl http://localhost:5001/auth/health
curl http://localhost:5002/api/health
curl http://localhost:5003/api/health

# 4. Run tests
./test_services.sh

# 5. View logs
docker-compose logs -f

# 6. Stop when done
docker-compose down
```

---

### Option 2: Kubernetes with Minikube

1. **Start Minikube:**
   ```bash
   minikube start
   ```

2. **Build Docker images (in Minikube's Docker environment):**
   ```bash
   eval $(minikube docker-env)

   # Build auth service
   cd auth-service
   docker build -t auth-service:latest .

   # Build business service
   cd ../business-service
   docker build -t business-service:latest .

   # Build queue service
   cd ../queue-service
   docker build -t queue-service:latest .
   ```

3. **Create shared directory in Minikube:**
   ```bash
   minikube ssh
   sudo mkdir -p /data/shared
   exit
   ```

4. **Copy shared code to Minikube:**
   ```bash
   cd ..
   minikube cp shared /data/shared
   ```

5. **Deploy to Kubernetes:**
   ```bash
   # Create namespace
   kubectl apply -f k8s/namespace.yaml

   # Deploy services
   kubectl apply -f k8s/auth-service-deployment.yaml -n nexturn
   kubectl apply -f k8s/business-service-deployment.yaml -n nexturn
   kubectl apply -f k8s/queue-service-deployment.yaml -n nexturn

   # Deploy ingress (optional)
   kubectl apply -f k8s/ingress.yaml -n nexturn
   ```

6. **Verify deployment:**
   ```bash
   kubectl get pods -n nexturn
   kubectl get services -n nexturn
   ```

7. **Access services (using port forwarding):**
   ```bash
   # Auth Service
   kubectl port-forward service/auth-service 5001:5001 -n nexturn

   # Business Service
   kubectl port-forward service/business-service 5002:5002 -n nexturn

   # Queue Service
   kubectl port-forward service/queue-service 5003:5003 -n nexturn
   ```

### Option 3: Run Services Locally (Development)

1. **Install dependencies for each service:**
   ```bash
   # Auth Service
   cd auth-service
   pip install -r requirements.txt
   python app/app.py

   # Business Service (in new terminal)
   cd business-service
   pip install -r requirements.txt
   python app/app.py

   # Queue Service (in new terminal)
   cd queue-service
   pip install -r requirements.txt
   python app/app.py
   ```

## 🌐 All Microservices - Ports & Status

| Service | Port | Status | Base URL | Health Check | Description |
|---------|------|--------|----------|--------------|-------------|
| **Auth Service** | 5001 | ✅ Implemented | http://localhost:5001 | /auth/health | User authentication & JWT tokens |
| **Business Service** | 5002 | ✅ Implemented | http://localhost:5002 | /api/health | Business registration & management |
| **Queue Service** | 5003 | ✅ Implemented | http://localhost:5003 | /api/health | Queue operations & ticket management |
| **Ticket Service** | 5004 | 🚧 Planned | http://localhost:5004 | /api/health | Advanced ticket operations & alerts |
| **Feedback Service** | 5005 | 🚧 Planned | http://localhost:5005 | /api/health | Customer feedback & ratings |
| **Analytics Service** | 5006 | 🚧 Planned | http://localhost:5006 | /api/health | Business analytics & insights |
| **Notification Service** | 5007 | 🚧 Planned | http://localhost:5007 | /api/health | Email/SMS/Push notifications |
| **API Gateway** | 8080 | 🚧 Planned | http://localhost:8080 | /health | Routing & load balancing |

## 🤖 Jenkins CI/CD

Each implemented microservice now ships with its own declarative Jenkins pipeline so you can build, test, package, and deploy services independently.

📖 **👉 [Complete Jenkins Setup Guide →](JENKINS_SETUP.md)** - Step-by-step instructions to install and configure Jenkins

### Pipeline files

| Service | Jenkinsfile path |
|---------|------------------|
| Auth | `microservices/auth-service/Jenkinsfile` |
| Business | `microservices/business-service/Jenkinsfile` |
| Queue | `microservices/queue-service/Jenkinsfile` |
| Frontend gateway | `microservices/frontend-service/Jenkinsfile` |

Create a Jenkins *Pipeline* (or Multibranch Pipeline) job per service and point it at the corresponding Jenkinsfile. The stages are consistent across services:

1. **Checkout** – pulls the repository.
2. **Setup Python environment** – creates a virtual environment and installs requirements + `pytest`.
3. **Unit tests** – runs pytest only if a `tests/` directory exists (can be skipped with the `RUN_TESTS` parameter).
4. **Docker build** – builds and tags an image using the service Dockerfile.
5. **Push image** *(optional)* – pushes to your registry when `PUSH_IMAGE=true`.
6. **Deploy to Minikube** *(optional)* – updates the matching Kubernetes deployment via `kubectl set image` when `DEPLOY_TO_MINIKUBE=true`.

### Required Jenkins tooling

- Docker CLI (to build/push images)
- Python 3.x (for virtualenv / pytest)
- kubectl + access to Minikube (only for deployment stage)

### Environment variables & credentials

Configure these in each Jenkins job (Manage Jenkins ➜ Credentials / job configuration):

| Variable | Purpose |
|----------|---------|
| `DOCKER_IMAGE_PREFIX` | Image prefix, e.g. `docker.io/username/nexturn` (default: `nexturn`). |
| `DOCKER_CREDENTIALS_ID` | Jenkins credential ID for Docker registry login (username/password). Required when pushing. |
| `DOCKER_LOGIN_SERVER` | Optional registry hostname passed to `docker login` (default: Docker Hub). |
| `KUBECONFIG_CREDENTIALS_ID` | Jenkins file credential containing kubeconfig for the Minikube cluster. Required when deploying. |
| `PYTHON_BIN` | Override Python binary name if `python3` is not available (default: `python3`). |

### Runtime parameters

Each Jenkinsfile exposes parameters you can toggle per run:

- `RUN_TESTS` – skip pytest when false.
- `PUSH_IMAGE` – enable/disable publishing to the registry.
- `DEPLOY_TO_MINIKUBE` – enable/disable `kubectl set image` rollout.
- `K8S_NAMESPACE` – namespace for rollout commands (defaults to `nexturn`).

### Suggested job names

```
NexTurn-auth-service
NexTurn-business-service
NexTurn-queue-service
NexTurn-frontend-service
```

Once the individual jobs are in place you can wire up a freestyle “umbrella” job (or use Jenkins Build Pipeline view) to trigger multiple services in parallel for a full release.

### 🔌 Current Service Endpoints (Implemented)

#### **Authentication Service (Port 5001)**
- `GET /` - Service info
- `GET /auth/health` - Health check
- `POST /auth/signup` - Register user
- `POST /auth/login` - Login & get JWT
- `GET /auth/verify` - Verify JWT token
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update profile

#### **Business Service (Port 5002)**
- `GET /` - Service info
- `GET /api/health` - Health check
- `POST /api/businesses` - Create business
- `GET /api/businesses` - List all businesses
- `GET /api/businesses/<id>` - Get business details
- `GET /api/businesses/my-businesses` - Get user's businesses
- `PUT /api/businesses/<id>` - Update business
- `DELETE /api/businesses/<id>` - Delete business
- `GET /api/businesses/<id>/stats` - Business statistics

#### **Queue Service (Port 5003)**
- `GET /` - Service info
- `GET /api/health` - Health check
- `POST /api/queues` - Create queue
- `GET /api/queues/<id>` - Get queue details
- `GET /api/queues/business/<id>` - Get business queues
- `PUT /api/queues/<id>` - Update queue
- `DELETE /api/queues/<id>` - Delete queue
- `POST /api/queues/<id>/join` - Join queue
- `GET /api/tickets/<id>` - Get ticket details
- `POST /api/tickets/<id>/cancel` - Cancel ticket
- `POST /api/queues/<id>/serve-next` - Serve next customer
- `GET /api/tickets/my-active` - Get active ticket
- `GET /api/tickets/my-history` - Get queue history

---

## 📖 API Documentation

### Authentication Service (Port 5001)

#### POST /auth/signup
Register a new user.

**Request:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "organization": "My Company"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 1
  },
  "message": "Account created successfully"
}
```

#### POST /auth/login
Login and receive JWT token.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "full_name": "John Doe",
      "email": "john@example.com",
      "organization": "My Company"
    }
  },
  "message": "Login successful"
}
```

#### GET /auth/verify
Verify JWT token (requires Authorization header).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "full_name": "John Doe",
      "email": "john@example.com",
      "organization": "My Company"
    }
  },
  "message": "Token is valid"
}
```

### Business Service (Port 5002)

#### POST /api/businesses
Create a new business (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "name": "Joe's Café",
  "description": "Best coffee in town",
  "category": "Café",
  "address": "123 Main St, City"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "business_id": 1
  },
  "message": "Business created successfully"
}
```

#### GET /api/businesses
Get all businesses.

**Response:**
```json
{
  "success": true,
  "data": {
    "businesses": [
      {
        "id": 1,
        "name": "Joe's Café",
        "description": "Best coffee in town",
        "category": "Café",
        "address": "123 Main St, City",
        "owner_id": 1,
        "created_at": "2025-11-18 12:00:00"
      }
    ]
  }
}
```

#### GET /api/businesses/my-businesses
Get businesses owned by authenticated user (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

### Queue Management Service (Port 5003)

#### POST /api/queues/<queue_id>/join
Join a queue (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
    "position": 3,
    "eta": 10,
    "queue_name": "Main Queue"
  },
  "message": "Joined queue successfully"
}
```

#### GET /api/tickets/<ticket_id>
Get ticket details (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ticket": {
      "id": 1,
      "queue_id": 1,
      "user_id": 1,
      "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
      "position": 3,
      "join_time": "2025-11-18 12:00:00",
      "status": "active",
      "eta": 10
    }
  }
}
```

#### GET /api/queues/business/<business_id>
Get all queues for a business.

**Response:**
```json
{
  "success": true,
  "data": {
    "queues": [
      {
        "id": 1,
        "business_id": 1,
        "name": "Main Queue",
        "avg_service_time": 5,
        "is_active": 1,
        "created_at": "2025-11-18 12:00:00",
        "size": 3
      }
    ]
  }
}
```

#### POST /api/queues/<queue_id>/serve-next
Serve next customer in queue (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "served_ticket": {
      "id": 1,
      "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": 1,
      "position": 1
    }
  },
  "message": "Customer served successfully"
}
```

## Testing

### Test with cURL

1. **Sign up:**
```bash
curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "confirm_password": "password123"
  }'
```

2. **Login:**
```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

3. **Create business (use token from login):**
```bash
curl -X POST http://localhost:5002/api/businesses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token_here>" \
  -d '{
    "name": "Joe'\''s Café",
    "description": "Best coffee in town",
    "category": "Café",
    "address": "123 Main St"
  }'
```

### Test with Postman

Import the following collection or create requests manually:
1. POST http://localhost:5001/auth/signup
2. POST http://localhost:5001/auth/login (save token)
3. POST http://localhost:5002/api/businesses (use Bearer token)
4. GET http://localhost:5002/api/businesses
5. POST http://localhost:5003/api/queues/1/join (use Bearer token)
6. GET http://localhost:5003/api/tickets/my-active (use Bearer token)

## Troubleshooting

### Docker Compose Issues

**Problem:** Services can't connect to each other
**Solution:** Ensure all services are on the same network (microservices-network)

**Problem:** Port already in use
**Solution:** Stop existing services or change ports in docker-compose.yml

### Kubernetes Issues

**Problem:** Pods are in CrashLoopBackOff
**Solution:** Check logs with `kubectl logs <pod-name> -n nexturn`

**Problem:** Services can't reach each other
**Solution:** Verify service names and ensure they're in the same namespace

**Problem:** Persistent volumes not working
**Solution:** Ensure Minikube has proper storage provisioner:
```bash
minikube addons enable default-storageclass
minikube addons enable storage-provisioner
```

### Shared Code Issues

**Problem:** ImportError: No module named 'database'
**Solution:** Ensure shared directory is properly mounted:
- Docker: Check volumes in docker-compose.yml
- Kubernetes: Ensure hostPath is configured correctly
- Local: Add shared to PYTHONPATH

## Monitoring

### Check Service Health

```bash
# Docker Compose
curl http://localhost:5001/auth/health
curl http://localhost:5002/api/health
curl http://localhost:5003/api/health

# Kubernetes
kubectl get pods -n nexturn
kubectl logs <pod-name> -n nexturn
kubectl describe pod <pod-name> -n nexturn
```

### View Logs

```bash
# Docker Compose
docker-compose logs -f auth-service
docker-compose logs -f business-service
docker-compose logs -f queue-service

# Kubernetes
kubectl logs -f deployment/auth-service -n nexturn
kubectl logs -f deployment/business-service -n nexturn
kubectl logs -f deployment/queue-service -n nexturn
```

## Scaling

### Docker Compose
```bash
docker-compose up --scale auth-service=3 --scale business-service=3
```

### Kubernetes
```bash
kubectl scale deployment auth-service --replicas=5 -n nexturn
kubectl scale deployment business-service --replicas=5 -n nexturn
kubectl scale deployment queue-service --replicas=5 -n nexturn
```

## Clean Up

### Docker Compose
```bash
docker-compose down -v
```

### Kubernetes
```bash
kubectl delete namespace nexturn
minikube stop
minikube delete
```

## Next Steps

1. Add API Gateway (Kong or Nginx)
2. Implement Feedback Service
3. Implement Analytics Service
4. Implement Notification Service
5. Add message queue (RabbitMQ/Kafka)
6. Add monitoring (Prometheus + Grafana)
7. Add centralized logging (ELK stack)
8. Add service mesh (Istio)

## Contributing

1. Create a new branch
2. Make changes
3. Test locally with Docker Compose
4. Test with Kubernetes/Minikube
5. Submit pull request

## License

MIT License
