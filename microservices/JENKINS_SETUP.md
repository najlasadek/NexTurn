# 🤖 Jenkins CI/CD Setup Guide

Complete step-by-step guide to set up Jenkins and configure it to build, test, and deploy NexTurn microservices.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Install Jenkins](#install-jenkins)
3. [Initial Jenkins Setup](#initial-jenkins-setup)
4. [Install Required Plugins](#install-required-plugins)
5. [Configure Tools](#configure-tools)
6. [Set Up Credentials](#set-up-credentials)
7. [Create Pipeline Jobs](#create-pipeline-jobs)
8. [Configure Pipeline Jobs](#configure-pipeline-jobs)
9. [Run Your First Build](#run-your-first-build)
10. [Troubleshooting](#troubleshooting)

---

## ✅ Prerequisites

Before starting, ensure you have:

- **Docker** installed and running
- **Git** installed
- **Minikube** installed (if deploying to Kubernetes)
- **kubectl** installed (if deploying to Kubernetes)
- **Python 3.x** installed (for running tests)
- **Internet connection** (for downloading Jenkins and plugins)

**Verify installations:**
```bash
docker --version
git --version
python3 --version
# If using Minikube:
minikube version
kubectl version --client
```

---

## 🐳 Install Jenkins

### Option 1: Run Jenkins in Docker (Recommended)

This is the easiest way to get Jenkins running:

```bash
# Create a directory for Jenkins data (persists across restarts)
mkdir -p ~/jenkins_home

# Run Jenkins container
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v ~/jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts

# View Jenkins logs
docker logs -f jenkins
```

**Important:** The `-v /var/run/docker.sock:/var/run/docker.sock` flag allows Jenkins to use Docker on your host machine.

**For Windows:**
```powershell
# Create Jenkins data directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\jenkins_home"

# Run Jenkins container
docker run -d `
  --name jenkins `
  -p 8080:8080 `
  -p 50000:50000 `
  -v "$env:USERPROFILE\jenkins_home:/var/jenkins_home" `
  -v //var/run/docker.sock:/var/run/docker.sock `
  jenkins/jenkins:lts
```

### Option 2: Install Jenkins on Your System

**Ubuntu/Debian:**
```bash
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

**macOS (Homebrew):**
```bash
brew install jenkins-lts
brew services start jenkins-lts
```

**Windows:**
Download and install from [jenkins.io/download](https://www.jenkins.io/download/)

---

## 🔐 Initial Jenkins Setup

1. **Open Jenkins in your browser:**
   ```
   http://localhost:8080
   ```

2. **Get the initial admin password:**
   
   **If using Docker:**
   ```bash
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```
   
   **If installed on system:**
   ```bash
   # Linux/macOS
   sudo cat /var/lib/jenkins/secrets/initialAdminPassword
   
   # Windows
   # Check: C:\Program Files\Jenkins\secrets\initialAdminPassword
   ```

3. **Paste the password** into Jenkins and click **Continue**

4. **Install suggested plugins:**
   - Click **"Install suggested plugins"**
   - Wait for installation to complete (5-10 minutes)

5. **Create admin user:**
   - Fill in the form with your details
   - Click **Save and Continue**

6. **Configure Jenkins URL:**
   - Keep default: `http://localhost:8080/`
   - Click **Save and Finish**

7. **Start using Jenkins:**
   - Click **Start using Jenkins**

---

## 🔌 Install Required Plugins

After initial setup, install additional plugins needed for the pipelines:

1. **Go to:** `Manage Jenkins` → `Plugins` → `Available plugins`

2. **Search and install these plugins:**
   - ✅ **Pipeline** (usually already installed)
   - ✅ **Docker Pipeline** - For Docker build steps
   - ✅ **Docker** - Docker integration
   - ✅ **Git** - Git integration
   - ✅ **Credentials Binding** - For secure credential management
   - ✅ **Pipeline Utility Steps** - Utility functions
   - ✅ **AnsiColor** - Colored console output
   - ✅ **Timestamper** - Timestamps in logs
   - ✅ **Kubernetes** (optional) - If deploying to Kubernetes
   - ✅ **Blue Ocean** (optional) - Modern UI for pipelines

3. **Click "Install without restart"** or **"Download now and install after restart"**

4. **Restart Jenkins** if prompted:
   ```bash
   # Docker
   docker restart jenkins
   
   # System service
   sudo systemctl restart jenkins
   ```

---

## 🛠️ Configure Tools

Configure tools that Jenkins will use:

### 1. Configure Docker

**If Jenkins is running in Docker:**
- Docker is already available via the mounted socket
- No additional configuration needed

**If Jenkins is installed on system:**
1. Go to: `Manage Jenkins` → `Configure System`
2. Scroll to **"Cloud"** section
3. Add Docker configuration if needed
4. Save

### 2. Configure Python

1. Go to: `Manage Jenkins` → `Global Tool Configuration`
2. Scroll to **"Python installations"**
3. Click **"Add Python"**
4. Configure:
   - **Name:** `Python3`
   - **Installation directory:** `/usr/bin/python3` (or wherever Python is installed)
   - Or check **"Install automatically"** to let Jenkins install it
5. Click **Save**

### 3. Configure Git

1. In **"Global Tool Configuration"**, scroll to **"Git installations"**
2. Add Git:
   - **Name:** `Default`
   - **Path to Git executable:** `/usr/bin/git` (or `git.exe` on Windows)
3. Click **Save**

---

## 🔑 Set Up Credentials

Create credentials that the pipelines will use:

### 1. Docker Registry Credentials (Optional - if pushing images)

1. Go to: `Manage Jenkins` → `Credentials` → `System` → `Global credentials`
2. Click **"Add Credentials"**
3. Configure:
   - **Kind:** `Username with password`
   - **Scope:** `Global`
   - **Username:** Your Docker Hub username (or registry username)
   - **Password:** Your Docker Hub password (or registry token)
   - **ID:** `docker-hub-credentials` (remember this ID!)
   - **Description:** `Docker Hub credentials for pushing images`
4. Click **OK**

### 2. Kubernetes kubeconfig (Optional - if deploying to Minikube)

1. **Get your kubeconfig:**
   ```bash
   # If using Minikube
   minikube config view
   kubectl config view --flatten > ~/kubeconfig
   ```

2. **In Jenkins:**
   - Go to: `Manage Jenkins` → `Credentials` → `System` → `Global credentials`
   - Click **"Add Credentials"**
   - Configure:
     - **Kind:** `Secret file`
     - **Scope:** `Global`
     - **File:** Upload your `kubeconfig` file
     - **ID:** `minikube-kubeconfig` (remember this ID!)
     - **Description:** `Minikube kubeconfig for deployments`
   - Click **OK**

### 3. Git Credentials (If repository is private)

1. Go to: `Manage Jenkins` → `Credentials` → `System` → `Global credentials`
2. Click **"Add Credentials"**
3. Configure:
   - **Kind:** `SSH Username with private key` or `Username with password`
   - **ID:** `git-credentials`
   - Enter your Git credentials
4. Click **OK**

---

## 📦 Create Pipeline Jobs

Create a pipeline job for each microservice:

### Method 1: Create Individual Pipeline Jobs

1. **Click "New Item"** on Jenkins dashboard

2. **For each service, create a new job:**
   - **Item name:** `auth-service-pipeline` (or `business-service-pipeline`, etc.)
   - **Type:** Select **"Pipeline"**
   - Click **OK**

3. **Repeat for all services:**
   - `auth-service-pipeline`
   - `business-service-pipeline`
   - `queue-service-pipeline`
   - `frontend-service-pipeline`

### Method 2: Create Multibranch Pipeline (Recommended)

This automatically creates jobs for each branch:

1. **Click "New Item"**
2. **Item name:** `nexturn-microservices`
3. **Type:** Select **"Multibranch Pipeline"**
4. Click **OK**

---

## ⚙️ Configure Pipeline Jobs

### For Individual Pipeline Jobs:

1. **Click on a job** (e.g., `auth-service-pipeline`)

2. **Click "Configure"**

3. **In "Pipeline" section:**
   - **Definition:** Select **"Pipeline script from SCM"**
   - **SCM:** Select **"Git"**
   - **Repository URL:** Enter your repository URL
     ```
     https://github.com/yourusername/NexTurn.git
     # or
     file:///path/to/NexTurn
     ```
   - **Credentials:** Select your Git credentials (if needed)
   - **Branches to build:** `*/main` or `*/master`
   - **Script Path:** `microservices/auth-service/Jenkinsfile`
     - For other services, use:
       - `microservices/business-service/Jenkinsfile`
       - `microservices/queue-service/Jenkinsfile`
       - `microservices/frontend-service/Jenkinsfile`

4. **In "Build Triggers" section (optional):**
   - ✅ **"Poll SCM"** - Check for changes periodically
     - Schedule: `H/5 * * * *` (every 5 minutes)
   - ✅ **"GitHub hook trigger"** - If using GitHub webhooks

5. **Click "Save"**

### For Multibranch Pipeline:

1. **Click "Configure"**

2. **In "Branch Sources" section:**
   - Click **"Add source"** → **"Git"**
   - **Project Repository:** Enter your repository URL
   - **Credentials:** Select Git credentials if needed

3. **In "Build Configuration" section:**
   - **Mode:** `by Jenkinsfile`
   - **Script Path:** Leave empty (will auto-detect)

4. **Click "Save"**

5. **Jenkins will scan branches** and create jobs automatically

---

## 🚀 Run Your First Build

### Manual Build:

1. **Go to Jenkins dashboard**
2. **Click on a pipeline job** (e.g., `auth-service-pipeline`)
3. **Click "Build with Parameters"** (if parameters are configured)
4. **Configure parameters:**
   - ✅ **RUN_TESTS:** `true` (or `false` to skip)
   - ✅ **PUSH_IMAGE:** `false` (set to `true` if you want to push)
   - ✅ **DEPLOY_TO_MINIKUBE:** `false` (set to `true` to deploy)
   - **K8S_NAMESPACE:** `nexturn`
5. **Click "Build"**

### View Build Progress:

1. **Click on the build number** in the build history
2. **Click "Console Output"** to see real-time logs
3. **Wait for build to complete** (5-15 minutes for first build)

### Expected Build Stages:

You should see these stages execute:
- ✅ **Checkout** - Clones repository
- ✅ **Setup Python environment** - Creates venv and installs dependencies
- ✅ **Unit tests** - Runs pytest (if tests exist)
- ✅ **Docker build** - Builds Docker image
- ✅ **Push image** - Pushes to registry (if enabled)
- ✅ **Deploy to Minikube** - Updates Kubernetes deployment (if enabled)

---

## 🔧 Configure Environment Variables

To customize pipeline behavior, set environment variables in Jenkins:

### Method 1: Global Environment Variables

1. Go to: `Manage Jenkins` → `Configure System`
2. Scroll to **"Global properties"**
3. Check **"Environment variables"**
4. Click **"Add"** and add:
   - **Name:** `DOCKER_IMAGE_PREFIX`
   - **Value:** `your-dockerhub-username/nexturn` (or your registry)
5. Click **Save**

### Method 2: Per-Job Environment Variables

1. **Open a pipeline job** → **Configure**
2. Scroll to **"Pipeline"** section
3. In the Jenkinsfile path, you can also add environment variables in the job configuration

### Recommended Environment Variables:

```bash
DOCKER_IMAGE_PREFIX=your-dockerhub-username/nexturn
DOCKER_CREDENTIALS_ID=docker-hub-credentials
DOCKER_LOGIN_SERVER=docker.io
KUBECONFIG_CREDENTIALS_ID=minikube-kubeconfig
PYTHON_BIN=python3
```

---

## 🎯 Quick Start Commands

### Start Jenkins (Docker):
```bash
docker start jenkins
# or if not created yet:
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 \
  -v ~/jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

### Stop Jenkins:
```bash
docker stop jenkins
```

### View Jenkins Logs:
```bash
docker logs -f jenkins
```

### Access Jenkins:
```
http://localhost:8080
```

### Get Admin Password:
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## 🐛 Troubleshooting

### Problem: Jenkins can't access Docker

**Solution:**
```bash
# Add Jenkins user to docker group (Linux)
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins

# Or ensure Docker socket is mounted (Docker)
docker run ... -v /var/run/docker.sock:/var/run/docker.sock ...
```

### Problem: "Permission denied" errors

**Solution:**
```bash
# Fix permissions for Jenkins home directory
sudo chown -R jenkins:jenkins /var/lib/jenkins
# or for Docker:
docker exec -u root jenkins chown -R jenkins:jenkins /var/jenkins_home
```

### Problem: Python not found

**Solution:**
- Install Python on Jenkins agent
- Or configure Python path in Jenkins Global Tool Configuration
- Or set `PYTHON_BIN` environment variable to correct path

### Problem: kubectl not found (when deploying)

**Solution:**
```bash
# Install kubectl on Jenkins agent
# Or use kubectl from a container in the pipeline
```

### Problem: Build fails at "Push image" stage

**Solution:**
- Verify Docker credentials are correct
- Check `DOCKER_CREDENTIALS_ID` matches credential ID in Jenkins
- Ensure you're logged into Docker registry:
  ```bash
  docker login
  ```

### Problem: Can't connect to Minikube

**Solution:**
```bash
# Ensure Minikube is running
minikube status

# Get kubeconfig
kubectl config view --flatten > kubeconfig

# Upload to Jenkins credentials
```

### Problem: Pipeline can't find Jenkinsfile

**Solution:**
- Verify repository URL is correct
- Check branch name matches
- Verify Script Path is correct (e.g., `microservices/auth-service/Jenkinsfile`)
- Ensure Jenkinsfile is committed to repository

---

## 📚 Next Steps

After setting up Jenkins:

1. ✅ **Test all pipeline jobs** - Run a build for each service
2. ✅ **Set up webhooks** - Automatically trigger builds on Git push
3. ✅ **Configure notifications** - Email/Slack notifications on build failure
4. ✅ **Set up Blue Ocean** - Modern UI for viewing pipelines
5. ✅ **Add more stages** - Linting, security scanning, etc.

---

## 📖 Additional Resources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-workflow/)
- [Kubernetes Plugin](https://plugins.jenkins.io/kubernetes/)

---

## ✅ Checklist

Use this checklist to verify your setup:

- [ ] Jenkins is installed and running
- [ ] Can access Jenkins at http://localhost:8080
- [ ] Required plugins are installed
- [ ] Docker is accessible from Jenkins
- [ ] Python is configured
- [ ] Git is configured
- [ ] Docker credentials are set up (if pushing images)
- [ ] Kubernetes kubeconfig is set up (if deploying)
- [ ] Pipeline jobs are created for all services
- [ ] Jobs are configured with correct Jenkinsfile paths
- [ ] First build completed successfully

---

**🎉 Congratulations!** You've successfully set up Jenkins CI/CD for NexTurn microservices!

For questions or issues, check the [Troubleshooting](#troubleshooting) section or refer to the main [README.md](README.md).

