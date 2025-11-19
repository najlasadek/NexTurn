# NexTurn Minikube Deployment Script (PowerShell)
# This script automates the deployment of NexTurn microservices to Minikube

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Check prerequisites
Write-Info "Checking prerequisites..."

$commands = @("minikube", "kubectl", "docker")
foreach ($cmd in $commands) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Error "$cmd is not installed. Please install it first."
        exit 1
    }
}

Write-Success "All prerequisites are installed"

# Start Minikube
Write-Info "Starting Minikube..."
$minikubeStatus = minikube status 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Warning "Minikube is already running"
} else {
    minikube start --memory=4096 --cpus=2
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to start Minikube"
        exit 1
    }
    Write-Success "Minikube started"
}

# Enable addons
Write-Info "Enabling Minikube addons..."
minikube addons enable ingress 2>$null
minikube addons enable default-storageclass 2>$null
minikube addons enable storage-provisioner 2>$null
Write-Success "Addons enabled"

# Configure Docker environment
Write-Info "Configuring Docker environment for Minikube..."
$dockerEnv = minikube docker-env | Out-String
Invoke-Expression $dockerEnv
Write-Success "Docker environment configured"

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Build Docker images
Write-Info "Building Docker images..."
Write-Info "This may take a few minutes..."

$services = @(
    @{Name="frontend-service"; Dockerfile="frontend-service/Dockerfile"; Context=".."},
    @{Name="auth-service"; Dockerfile="auth-service/Dockerfile"; Context="."},
    @{Name="business-service"; Dockerfile="business-service/Dockerfile"; Context="."},
    @{Name="queue-service"; Dockerfile="queue-service/Dockerfile"; Context="."},
    @{Name="feedback-service"; Dockerfile="feedback-service/Dockerfile"; Context="."},
    @{Name="ticket-service"; Dockerfile="ticket-service/Dockerfile"; Context="."},
    @{Name="analytics-service"; Dockerfile="analytics-service/Dockerfile"; Context="."},
    @{Name="notification-service"; Dockerfile="notification-service/Dockerfile"; Context="."}
)

foreach ($service in $services) {
    Write-Info "Building $($service.Name)..."
    docker build -f $service.Dockerfile -t "$($service.Name):latest" $service.Context 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build $($service.Name)"
        exit 1
    }
    Write-Success "$($service.Name) built"
}

Write-Success "All Docker images built successfully"

# Create namespace
Write-Info "Creating namespace..."
kubectl apply -f k8s/namespace.yaml 2>&1 | Out-Null
Write-Success "Namespace created"

# Deploy services
Write-Info "Deploying services to Kubernetes..."

# Deploy core services first
Write-Info "Deploying core services (auth, business, queue)..."
kubectl apply -f k8s/auth-service-deployment.yaml 2>&1 | Out-Null
kubectl apply -f k8s/business-service-deployment.yaml 2>&1 | Out-Null
kubectl apply -f k8s/queue-service-deployment.yaml 2>&1 | Out-Null

# Deploy additional services
Write-Info "Deploying additional services..."
kubectl apply -f k8s/frontend-service-deployment.yaml 2>&1 | Out-Null
kubectl apply -f k8s/feedback-service-deployment.yaml 2>&1 | Out-Null
kubectl apply -f k8s/ticket-service-deployment.yaml 2>&1 | Out-Null
kubectl apply -f k8s/analytics-service-deployment.yaml 2>&1 | Out-Null
kubectl apply -f k8s/notification-service-deployment.yaml 2>&1 | Out-Null

# Deploy ingress (optional)
Write-Info "Deploying ingress..."
kubectl apply -f k8s/ingress.yaml 2>&1 | Out-Null

Write-Success "All services deployed"

# Wait for pods to be ready
Write-Info "Waiting for pods to be ready..."
Start-Sleep -Seconds 5

# Check pod status
Write-Info "Checking pod status..."
kubectl get pods -n nexturn

# Wait for all pods to be running
Write-Info "Waiting for all pods to be in Running state..."
$timeout = 300  # 5 minutes
$elapsed = 0
$allReady = $false

while ($elapsed -lt $timeout) {
    $pods = kubectl get pods -n nexturn --no-headers 2>&1
    if ($LASTEXITCODE -eq 0) {
        $running = ($pods | Select-String "Running").Count
        $total = ($pods | Measure-Object -Line).Lines
        
        if ($running -eq $total -and $total -gt 0) {
            Write-Success "All pods are running!"
            $allReady = $true
            break
        }
    }
    
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 5
    $elapsed += 5
}

Write-Host ""

if (-not $allReady) {
    Write-Warning "Timeout waiting for pods. Some pods may still be starting."
    Write-Info "Check pod status with: kubectl get pods -n nexturn"
}

# Display service information
Write-Host ""
Write-Success "Deployment completed!"
Write-Host ""
Write-Info "Service Status:"
kubectl get services -n nexturn
Write-Host ""
Write-Info "Pod Status:"
kubectl get pods -n nexturn
Write-Host ""

# Display access information
Write-Info "To access services, use port forwarding:"
Write-Host ""
Write-Host "  # Frontend Service"
Write-Host "  kubectl port-forward service/frontend-service 5000:5000 -n nexturn"
Write-Host ""
Write-Host "  # Auth Service"
Write-Host "  kubectl port-forward service/auth-service 5001:5001 -n nexturn"
Write-Host ""
Write-Host "  # Business Service"
Write-Host "  kubectl port-forward service/business-service 5002:5002 -n nexturn"
Write-Host ""
Write-Host "  # Queue Service"
Write-Host "  kubectl port-forward service/queue-service 5003:5003 -n nexturn"
Write-Host ""

Write-Info "View logs with:"
Write-Host "  kubectl logs -f deployment/<service-name> -n nexturn"
Write-Host ""

Write-Info "For more information, see MINIKUBE_DEPLOYMENT.md"
Write-Host ""

Write-Success "Deployment script completed successfully! 🚀"

