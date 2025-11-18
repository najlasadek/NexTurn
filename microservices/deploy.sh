#!/bin/bash

# NexTurn Microservices Deployment Script

echo "🚀 NexTurn Microservices Deployment Script"
echo "==========================================="

# Function to deploy with Docker Compose
deploy_docker_compose() {
    echo ""
    echo "📦 Deploying with Docker Compose..."
    docker-compose up --build -d

    echo ""
    echo "✅ Services deployed!"
    echo ""
    echo "🔗 Service URLs:"
    echo "   Auth Service: http://localhost:5001"
    echo "   Business Service: http://localhost:5002"
    echo "   Queue Service: http://localhost:5003"
    echo ""
    echo "📊 Check status: docker-compose ps"
    echo "📝 View logs: docker-compose logs -f"
    echo "🛑 Stop services: docker-compose down"
}

# Function to deploy with Kubernetes
deploy_kubernetes() {
    echo ""
    echo "☸️  Deploying with Kubernetes (Minikube)..."

    # Check if Minikube is running
    if ! minikube status > /dev/null 2>&1; then
        echo "⚠️  Minikube is not running. Starting Minikube..."
        minikube start
    fi

    # Use Minikube's Docker daemon
    eval $(minikube docker-env)

    echo ""
    echo "🏗️  Building Docker images..."

    # Build auth service
    echo "  Building auth-service..."
    cd auth-service
    docker build -t auth-service:latest . -q
    cd ..

    # Build business service
    echo "  Building business-service..."
    cd business-service
    docker build -t business-service:latest . -q
    cd ..

    # Build queue service
    echo "  Building queue-service..."
    cd queue-service
    docker build -t queue-service:latest . -q
    cd ..

    echo ""
    echo "📂 Setting up shared directory..."
    minikube ssh "sudo mkdir -p /data/shared" 2>/dev/null

    echo ""
    echo "🚢 Deploying to Kubernetes..."

    # Create namespace
    kubectl apply -f k8s/namespace.yaml

    # Deploy services
    kubectl apply -f k8s/auth-service-deployment.yaml -n nexturn
    kubectl apply -f k8s/business-service-deployment.yaml -n nexturn
    kubectl apply -f k8s/queue-service-deployment.yaml -n nexturn

    echo ""
    echo "⏳ Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=auth-service -n nexturn --timeout=120s 2>/dev/null
    kubectl wait --for=condition=ready pod -l app=business-service -n nexturn --timeout=120s 2>/dev/null
    kubectl wait --for=condition=ready pod -l app=queue-service -n nexturn --timeout=120s 2>/dev/null

    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📊 Pod Status:"
    kubectl get pods -n nexturn
    echo ""
    echo "🔗 Access services with port forwarding:"
    echo "   kubectl port-forward service/auth-service 5001:5001 -n nexturn"
    echo "   kubectl port-forward service/business-service 5002:5002 -n nexturn"
    echo "   kubectl port-forward service/queue-service 5003:5003 -n nexturn"
    echo ""
    echo "📝 View logs:"
    echo "   kubectl logs -f deployment/auth-service -n nexturn"
    echo "   kubectl logs -f deployment/business-service -n nexturn"
    echo "   kubectl logs -f deployment/queue-service -n nexturn"
}

# Main menu
echo ""
echo "Select deployment method:"
echo "1) Docker Compose (recommended for development)"
echo "2) Kubernetes with Minikube (for learning K8s)"
echo "3) Exit"
echo ""
read -p "Enter your choice [1-3]: " choice

case $choice in
    1)
        deploy_docker_compose
        ;;
    2)
        deploy_kubernetes
        ;;
    3)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment complete!"
