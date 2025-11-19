# 🚀 Deploying NexTurn on Minikube

This guide will walk you through deploying the NexTurn microservices architecture on Minikube.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1. **Minikube** - [Installation Guide](https://minikube.sigs.k8s.io/docs/start/)
2. **kubectl** - [Installation Guide](https://kubernetes.io/docs/tasks/tools/)
3. **Docker** - [Installation Guide](https://docs.docker.com/get-docker/)

### Verify Installation

```bash
# Check Minikube version
minikube version

# Check kubectl version
kubectl version --client

# Check Docker version
docker --version
```

## 🎯 Quick Start (Automated)

The easiest way to deploy is using the provided deployment script:

```bash
cd microservices
chmod +x deploy-minikube.sh
./deploy-minikube.sh
```

This script will:
- Start Minikube
- Build all Docker images
- Deploy all services to Kubernetes
- Set up port forwarding
- Show you how to access the services

## 📖 Manual Deployment Steps

If you prefer to deploy manually, follow these steps:

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --memory=4096 --cpus=2

# Verify Minikube is running
minikube status

# Enable required addons
minikube addons enable ingress
minikube addons enable default-storageclass
minikube addons enable storage-provisioner
```

### Step 2: Configure Docker Environment

Minikube has its own Docker daemon. You need to use it to build images:

```bash
# Point Docker to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify you're using Minikube's Docker
docker info | grep "Operating System"
```

**Note:** Keep this terminal session open. If you open a new terminal, run `eval $(minikube docker-env)` again.

### Step 3: Build Docker Images

Build all service images:

```bash
# Navigate to microservices directory
cd microservices

# Build frontend service
docker build -f frontend-service/Dockerfile -t frontend-service:latest ..

# Build auth service
docker build -f auth-service/Dockerfile -t auth-service:latest .

# Build business service
docker build -f business-service/Dockerfile -t business-service:latest .

# Build queue service
docker build -f queue-service/Dockerfile -t queue-service:latest .

# Build feedback service
docker build -f feedback-service/Dockerfile -t feedback-service:latest .

# Build ticket service
docker build -f ticket-service/Dockerfile -t ticket-service:latest .

# Build analytics service
docker build -f analytics-service/Dockerfile -t analytics-service:latest .

# Build notification service
docker build -f notification-service/Dockerfile -t notification-service:latest .
```

**Verify images are built:**
```bash
docker images | grep -E "(frontend|auth|business|queue|feedback|ticket|analytics|notification)-service"
```

### Step 4: Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### Step 5: Deploy Services

Deploy all services in order:

```bash
# Deploy core services first
kubectl apply -f k8s/auth-service-deployment.yaml
kubectl apply -f k8s/business-service-deployment.yaml
kubectl apply -f k8s/queue-service-deployment.yaml

# Deploy additional services
kubectl apply -f k8s/frontend-service-deployment.yaml
kubectl apply -f k8s/feedback-service-deployment.yaml
kubectl apply -f k8s/ticket-service-deployment.yaml
kubectl apply -f k8s/analytics-service-deployment.yaml
kubectl apply -f k8s/notification-service-deployment.yaml

# Deploy ingress (optional)
kubectl apply -f k8s/ingress.yaml
```

**Or deploy all at once:**
```bash
kubectl apply -f k8s/
```

### Step 6: Verify Deployment

Check that all pods are running:

```bash
# Check pod status
kubectl get pods -n nexturn

# Watch pods until all are Running
kubectl get pods -n nexturn -w
```

**Expected output:**
```
NAME                                  READY   STATUS    RESTARTS   AGE
auth-service-xxxxxxxxxx-xxxxx         1/1     Running   0          2m
business-service-xxxxxxxxxx-xxxxx     1/1     Running   0          2m
queue-service-xxxxxxxxxx-xxxxx        1/1     Running   0          2m
frontend-service-xxxxxxxxxx-xxxxx     1/1     Running   0          1m
feedback-service-xxxxxxxxxx-xxxxx     1/1     Running   0          1m
ticket-service-xxxxxxxxxx-xxxxx       1/1     Running   0          1m
analytics-service-xxxxxxxxxx-xxxxx    1/1     Running   0          1m
notification-service-xxxxxxxxxx-xxxxx 1/1     Running   0          1m
```

Check services:

```bash
kubectl get services -n nexturn
```

### Step 7: Access Services

#### Option 1: Port Forwarding (Recommended for Testing)

Open multiple terminal windows and run:

```bash
# Terminal 1 - Frontend
kubectl port-forward service/frontend-service 5000:5000 -n nexturn

# Terminal 2 - Auth Service
kubectl port-forward service/auth-service 5001:5001 -n nexturn

# Terminal 3 - Business Service
kubectl port-forward service/business-service 5002:5002 -n nexturn

# Terminal 4 - Queue Service
kubectl port-forward service/queue-service 5003:5003 -n nexturn
```

Then access services at:
- Frontend: http://localhost:5000
- Auth Service: http://localhost:5001
- Business Service: http://localhost:5002
- Queue Service: http://localhost:5003

#### Option 2: Minikube Service (For NodePort Services)

If you change services to NodePort type, you can use:

```bash
# Get service URL
minikube service frontend-service -n nexturn
```

#### Option 3: Ingress (Requires Ingress Controller)

If you've enabled ingress:

```bash
# Get ingress IP
minikube ip

# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
# <minikube-ip> nexturn.local
```

Then access at: http://nexturn.local

### Step 8: Test Services

Test health endpoints:

```bash
# Frontend
curl http://localhost:5000/health

# Auth Service
curl http://localhost:5001/auth/health

# Business Service
curl http://localhost:5002/api/health

# Queue Service
curl http://localhost:5003/api/health
```

## 🔍 Monitoring and Debugging

### View Logs

```bash
# View logs for a specific service
kubectl logs -f deployment/auth-service -n nexturn

# View logs for all pods
kubectl logs -f -l app=auth-service -n nexturn

# View logs for a specific pod
kubectl logs <pod-name> -n nexturn
```

### Check Pod Status

```bash
# Get detailed pod information
kubectl describe pod <pod-name> -n nexturn

# Get pod events
kubectl get events -n nexturn --sort-by='.lastTimestamp'
```

### Check Service Endpoints

```bash
# Verify service endpoints
kubectl get endpoints -n nexturn

# Test service connectivity from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -n nexturn -- wget -qO- http://auth-service:5001/auth/health
```

### Common Issues

#### Pods in CrashLoopBackOff

```bash
# Check pod logs
kubectl logs <pod-name> -n nexturn

# Check pod description
kubectl describe pod <pod-name> -n nexturn

# Common causes:
# - Image not found (check imagePullPolicy: Never)
# - Database initialization issues
# - Missing environment variables
```

#### Services Can't Connect

```bash
# Verify services are in the same namespace
kubectl get services -n nexturn

# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -n nexturn -- nslookup auth-service
```

#### Persistent Volume Issues

```bash
# Check PVC status
kubectl get pvc -n nexturn

# Check PV status
kubectl get pv

# Describe PVC for details
kubectl describe pvc auth-db-pvc -n nexturn
```

## 📊 Scaling Services

Scale services up or down:

```bash
# Scale auth service to 3 replicas
kubectl scale deployment auth-service --replicas=3 -n nexturn

# Scale business service to 5 replicas
kubectl scale deployment business-service --replicas=5 -n nexturn

# Check scaling status
kubectl get deployments -n nexturn
```

## 🔄 Updating Services

### Update Image

```bash
# Rebuild image
docker build -f auth-service/Dockerfile -t auth-service:latest .

# Restart deployment
kubectl rollout restart deployment/auth-service -n nexturn

# Or delete pod to force recreation
kubectl delete pod -l app=auth-service -n nexturn
```

### Update Configuration

```bash
# Edit deployment
kubectl edit deployment auth-service -n nexturn

# Apply updated manifest
kubectl apply -f k8s/auth-service-deployment.yaml

# Check rollout status
kubectl rollout status deployment/auth-service -n nexturn
```

## 🧹 Cleanup

### Remove All Resources

```bash
# Delete all resources in namespace
kubectl delete namespace nexturn

# Or delete individual resources
kubectl delete -f k8s/
```

### Stop Minikube

```bash
# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

### Reset Docker Environment

```bash
# Unset Minikube Docker environment
eval $(minikube docker-env -u)
```

## 📝 Service URLs Reference

| Service | Port | Internal URL | External (Port Forward) |
|---------|------|--------------|-------------------------|
| Frontend | 5000 | http://frontend-service:5000 | http://localhost:5000 |
| Auth | 5001 | http://auth-service:5001 | http://localhost:5001 |
| Business | 5002 | http://business-service:5002 | http://localhost:5002 |
| Queue | 5003 | http://queue-service:5003 | http://localhost:5003 |
| Ticket | 5004 | http://ticket-service:5004 | http://localhost:5004 |
| Feedback | 5005 | http://feedback-service:5005 | http://localhost:5005 |
| Analytics | 5006 | http://analytics-service:5006 | http://localhost:5006 |
| Notification | 5007 | http://notification-service:5007 | http://localhost:5007 |

## 🎓 Next Steps

1. **Set up monitoring** - Add Prometheus and Grafana
2. **Configure logging** - Set up centralized logging with ELK stack
3. **Add CI/CD** - Automate builds and deployments
4. **Implement service mesh** - Add Istio for advanced traffic management
5. **Set up secrets management** - Use Kubernetes Secrets or external secret managers

## 🆘 Troubleshooting

### Minikube won't start

```bash
# Check system requirements
minikube start --driver=docker --memory=4096 --cpus=2

# If issues persist, try different driver
minikube start --driver=hyperv  # Windows
minikube start --driver=virtualbox  # Linux/Mac
```

### Images not found

```bash
# Ensure you're using Minikube's Docker
eval $(minikube docker-env)

# Verify images exist
docker images | grep service

# Check imagePullPolicy in manifests (should be Never for local images)
```

### Port forwarding fails

```bash
# Check if service exists
kubectl get services -n nexturn

# Check if pods are running
kubectl get pods -n nexturn

# Try different port
kubectl port-forward service/auth-service 8080:5001 -n nexturn
```

## 📚 Additional Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

---

**Happy Deploying! 🚀**

