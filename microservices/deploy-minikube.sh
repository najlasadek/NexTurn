#!/bin/bash

# NexTurn Minikube Deployment Script
# This script automates the deployment of NexTurn microservices to Minikube

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_info "Checking prerequisites..."

if ! command_exists minikube; then
    print_error "Minikube is not installed. Please install it first."
    exit 1
fi

if ! command_exists kubectl; then
    print_error "kubectl is not installed. Please install it first."
    exit 1
fi

if ! command_exists docker; then
    print_error "Docker is not installed. Please install it first."
    exit 1
fi

print_success "All prerequisites are installed"

# Start Minikube
print_info "Starting Minikube..."
if minikube status >/dev/null 2>&1; then
    print_warning "Minikube is already running"
else
    minikube start --memory=4096 --cpus=2
    print_success "Minikube started"
fi

# Enable addons
print_info "Enabling Minikube addons..."
minikube addons enable ingress 2>/dev/null || true
minikube addons enable default-storageclass 2>/dev/null || true
minikube addons enable storage-provisioner 2>/dev/null || true
print_success "Addons enabled"

# Configure Docker environment
print_info "Configuring Docker environment for Minikube..."
eval $(minikube docker-env)
print_success "Docker environment configured"

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Build Docker images
print_info "Building Docker images..."
print_info "This may take a few minutes..."

# Build frontend service
print_info "Building frontend-service..."
docker build -f frontend-service/Dockerfile -t frontend-service:latest .. >/dev/null 2>&1 || {
    print_error "Failed to build frontend-service"
    exit 1
}
print_success "frontend-service built"

# Build auth service
print_info "Building auth-service..."
docker build -f auth-service/Dockerfile -t auth-service:latest . >/dev/null 2>&1 || {
    print_error "Failed to build auth-service"
    exit 1
}
print_success "auth-service built"

# Build business service
print_info "Building business-service..."
docker build -f business-service/Dockerfile -t business-service:latest . >/dev/null 2>&1 || {
    print_error "Failed to build business-service"
    exit 1
}
print_success "business-service built"

# Build queue service
print_info "Building queue-service..."
docker build -f queue-service/Dockerfile -t queue-service:latest . >/dev/null 2>&1 || {
    print_error "Failed to build queue-service"
    exit 1
}
print_success "queue-service built"

# Build feedback service
print_info "Building feedback-service..."
docker build -f feedback-service/Dockerfile -t feedback-service:latest . >/dev/null 2>&1 || {
    print_error "Failed to build feedback-service"
    exit 1
}
print_success "feedback-service built"

# Build ticket service
print_info "Building ticket-service..."
docker build -f ticket-service/Dockerfile -t ticket-service:latest . >/dev/null 2>&1 || {
    print_error "Failed to build ticket-service"
    exit 1
}
print_success "ticket-service built"

# Build analytics service
print_info "Building analytics-service..."
docker build -f analytics-service/Dockerfile -t analytics-service:latest . >/dev/null 2>&1 || {
    print_error "Failed to build analytics-service"
    exit 1
}
print_success "analytics-service built"

# Build notification service
print_info "Building notification-service..."
docker build -f notification-service/Dockerfile -t notification-service:latest . >/dev/null 2>&1 || {
    print_error "Failed to build notification-service"
    exit 1
}
print_success "notification-service built"

print_success "All Docker images built successfully"

# Create namespace
print_info "Creating namespace..."
kubectl apply -f k8s/namespace.yaml >/dev/null 2>&1 || true
print_success "Namespace created"

# Deploy services
print_info "Deploying services to Kubernetes..."

# Deploy core services first
print_info "Deploying core services (auth, business, queue)..."
kubectl apply -f k8s/auth-service-deployment.yaml >/dev/null 2>&1
kubectl apply -f k8s/business-service-deployment.yaml >/dev/null 2>&1
kubectl apply -f k8s/queue-service-deployment.yaml >/dev/null 2>&1

# Deploy additional services
print_info "Deploying additional services..."
kubectl apply -f k8s/frontend-service-deployment.yaml >/dev/null 2>&1
kubectl apply -f k8s/feedback-service-deployment.yaml >/dev/null 2>&1
kubectl apply -f k8s/ticket-service-deployment.yaml >/dev/null 2>&1
kubectl apply -f k8s/analytics-service-deployment.yaml >/dev/null 2>&1
kubectl apply -f k8s/notification-service-deployment.yaml >/dev/null 2>&1

# Deploy ingress (optional)
print_info "Deploying ingress..."
kubectl apply -f k8s/ingress.yaml >/dev/null 2>&1 || true

print_success "All services deployed"

# Wait for pods to be ready
print_info "Waiting for pods to be ready..."
sleep 5

# Check pod status
print_info "Checking pod status..."
kubectl get pods -n nexturn

# Wait for all pods to be running
print_info "Waiting for all pods to be in Running state..."
TIMEOUT=300  # 5 minutes
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    READY=$(kubectl get pods -n nexturn --no-headers 2>/dev/null | grep -c "Running" || echo "0")
    TOTAL=$(kubectl get pods -n nexturn --no-headers 2>/dev/null | wc -l | tr -d ' ')
    
    if [ "$READY" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
        print_success "All pods are running!"
        break
    fi
    
    echo -n "."
    sleep 5
    ELAPSED=$((ELAPSED + 5))
done

echo ""

if [ $ELAPSED -ge $TIMEOUT ]; then
    print_warning "Timeout waiting for pods. Some pods may still be starting."
    print_info "Check pod status with: kubectl get pods -n nexturn"
fi

# Display service information
echo ""
print_success "Deployment completed!"
echo ""
print_info "Service Status:"
kubectl get services -n nexturn
echo ""
print_info "Pod Status:"
kubectl get pods -n nexturn
echo ""

# Display access information
print_info "To access services, use port forwarding:"
echo ""
echo "  # Frontend Service"
echo "  kubectl port-forward service/frontend-service 5000:5000 -n nexturn"
echo ""
echo "  # Auth Service"
echo "  kubectl port-forward service/auth-service 5001:5001 -n nexturn"
echo ""
echo "  # Business Service"
echo "  kubectl port-forward service/business-service 5002:5002 -n nexturn"
echo ""
echo "  # Queue Service"
echo "  kubectl port-forward service/queue-service 5003:5003 -n nexturn"
echo ""

print_info "View logs with:"
echo "  kubectl logs -f deployment/<service-name> -n nexturn"
echo ""

print_info "For more information, see MINIKUBE_DEPLOYMENT.md"
echo ""

print_success "Deployment script completed successfully! 🚀"

