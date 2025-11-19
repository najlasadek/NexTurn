# Kubernetes Manifests for NexTurn

This directory contains all Kubernetes manifests needed to deploy NexTurn microservices to Minikube or any Kubernetes cluster.

## 📁 Files Overview

| File | Description |
|------|-------------|
| `namespace.yaml` | Creates the `nexturn` namespace |
| `auth-service-deployment.yaml` | Auth service deployment, service, and PVC |
| `business-service-deployment.yaml` | Business service deployment, service, and PVC |
| `queue-service-deployment.yaml` | Queue service deployment, service, and PVC |
| `frontend-service-deployment.yaml` | Frontend service deployment and service |
| `feedback-service-deployment.yaml` | Feedback service deployment, service, and PVC |
| `ticket-service-deployment.yaml` | Ticket service deployment, service, and PVC |
| `analytics-service-deployment.yaml` | Analytics service deployment, service, and PVC |
| `notification-service-deployment.yaml` | Notification service deployment, service, and PVC |
| `ingress.yaml` | Ingress configuration for external access |

## 🚀 Quick Deploy

### Using the deployment script (Recommended)

**Linux/Mac:**
```bash
chmod +x deploy-minikube.sh
./deploy-minikube.sh
```

**Windows (PowerShell):**
```powershell
.\deploy-minikube.ps1
```

### Manual deployment

```bash
# 1. Create namespace
kubectl apply -f namespace.yaml

# 2. Deploy all services
kubectl apply -f .

# 3. Check status
kubectl get pods -n nexturn
kubectl get services -n nexturn
```

## 📋 Deployment Order

Services should be deployed in this order for best results:

1. **Namespace** - `namespace.yaml`
2. **Core Services** - `auth-service-deployment.yaml`, `business-service-deployment.yaml`, `queue-service-deployment.yaml`
3. **Additional Services** - `frontend-service-deployment.yaml`, `feedback-service-deployment.yaml`, `ticket-service-deployment.yaml`, `analytics-service-deployment.yaml`, `notification-service-deployment.yaml`
4. **Ingress** (Optional) - `ingress.yaml`

## 🔧 Configuration

### Image Pull Policy

All manifests use `imagePullPolicy: Never` which means Kubernetes will use locally built images. This is required for Minikube deployments where images are built locally.

For production deployments, change this to:
- `imagePullPolicy: Always` - Always pull latest image
- `imagePullPolicy: IfNotPresent` - Pull only if not present locally

### Resource Limits

Each service has resource requests and limits configured:
- **Requests**: Minimum resources guaranteed
- **Limits**: Maximum resources allowed

Adjust these based on your cluster capacity and service requirements.

### Persistent Volumes

Services with databases use PersistentVolumeClaims (PVCs) for data persistence:
- `auth-db-pvc` - Auth service database
- `business-db-pvc` - Business service database
- `queue-db-pvc` - Queue service database
- `feedback-db-pvc` - Feedback service database
- `ticket-db-pvc` - Ticket service database
- `analytics-db-pvc` - Analytics service database
- `notification-db-pvc` - Notification service database

Each PVC requests 1Gi of storage. Adjust based on your needs.

### Environment Variables

Key environment variables configured:
- `JWT_SECRET_KEY` - Secret key for JWT tokens (change in production!)
- `PYTHONPATH` - Python path for imports
- Service URLs for inter-service communication

## 🌐 Service Discovery

Services communicate using Kubernetes DNS:
- `auth-service:5001` - Auth service
- `business-service:5002` - Business service
- `queue-service:5003` - Queue service
- `frontend-service:5000` - Frontend service
- `feedback-service:5005` - Feedback service
- `ticket-service:5004` - Ticket service
- `analytics-service:5006` - Analytics service
- `notification-service:5007` - Notification service

## 📊 Scaling

Scale services using kubectl:

```bash
# Scale auth service to 3 replicas
kubectl scale deployment auth-service --replicas=3 -n nexturn

# Scale all services
kubectl scale deployment --all --replicas=3 -n nexturn
```

Or edit the deployment files and change the `replicas` field.

## 🔍 Monitoring

### Check Pod Status
```bash
kubectl get pods -n nexturn
kubectl describe pod <pod-name> -n nexturn
```

### View Logs
```bash
kubectl logs -f deployment/auth-service -n nexturn
kubectl logs -f -l app=auth-service -n nexturn
```

### Check Services
```bash
kubectl get services -n nexturn
kubectl describe service auth-service -n nexturn
```

### Check PVCs
```bash
kubectl get pvc -n nexturn
kubectl describe pvc auth-db-pvc -n nexturn
```

## 🧹 Cleanup

Remove all resources:

```bash
# Delete all resources in namespace
kubectl delete namespace nexturn

# Or delete individual resources
kubectl delete -f .
```

## 📝 Notes

- All services are deployed in the `nexturn` namespace
- Services use ClusterIP type (internal only)
- For external access, use port-forwarding or ingress
- Health checks are configured for all services
- Liveness and readiness probes ensure service reliability

## 🔗 Related Documentation

- [MINIKUBE_DEPLOYMENT.md](../MINIKUBE_DEPLOYMENT.md) - Complete deployment guide
- [README.md](../README.md) - Main project documentation

