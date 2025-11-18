# 🚀 How to Run NexTurn Microservices

## ✅ Prerequisites Checklist

Before starting, make sure you have:
- [ ] Docker Desktop installed and running
- [ ] Git Bash or Terminal open
- [ ] Internet connection (for downloading dependencies)

**How to check if Docker is running:**
```bash
docker --version
docker-compose --version
```

You should see version numbers. If not, install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

---

## 🎯 Quick Start (3 Commands!)

### **Step 1: Open Terminal**
Open Git Bash (Windows) or Terminal (Mac/Linux)

### **Step 2: Navigate to microservices folder**
```bash
cd NexTurn/microservices
```

### **Step 3: Start all services**
```bash
docker-compose up --build
```

**That's it!** All 3 services are now running! 🎉

---

## 📺 What You'll See

When you run `docker-compose up --build`, you'll see:

```
[+] Building 45.2s (24/24) FINISHED
 => [auth-service internal] load build definition
 => [business-service internal] load build definition
 => [queue-service internal] load build definition
...
[+] Running 3/3
 ✔ Container auth-service      Started
 ✔ Container business-service  Started
 ✔ Container queue-service     Started

Attaching to auth-service, business-service, queue-service
auth-service      | 🔐 Authentication Service starting on port 5001...
auth-service      |  * Running on all addresses (0.0.0.0)
auth-service      |  * Running on http://127.0.0.1:5001
business-service  | 🏢 Business Service starting on port 5002...
business-service  |  * Running on all addresses (0.0.0.0)
business-service  |  * Running on http://127.0.0.1:5002
queue-service     | 📋 Queue Management Service starting on port 5003...
queue-service     |  * Running on all addresses (0.0.0.0)
queue-service     |  * Running on http://127.0.0.1:5003
```

---

## ✅ Verify Services Are Running

### **Option 1: Check in Browser**

Open these URLs in your browser:
- http://localhost:5001 - Auth Service
- http://localhost:5002 - Business Service
- http://localhost:5003 - Queue Service

You should see JSON with service information.

### **Option 2: Check with cURL**

In a **NEW terminal** (keep the first one running), run:

```bash
# Check Auth Service
curl http://localhost:5001/auth/health

# Check Business Service
curl http://localhost:5002/api/health

# Check Queue Service
curl http://localhost:5003/api/health
```

**Expected response for each:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "auth-service"
  }
}
```

### **Option 3: Check with Docker**

In a **NEW terminal**:

```bash
docker-compose ps
```

**Expected output:**
```
NAME                  STATUS          PORTS
auth-service          Up 2 minutes    0.0.0.0:5001->5001/tcp
business-service      Up 2 minutes    0.0.0.0:5002->5002/tcp
queue-service         Up 2 minutes    0.0.0.0:5003->5003/tcp
```

All should show "Up" status.

---

## 🧪 Test the Services

### **Automated Tests (Recommended)**

In a **NEW terminal** (while services are running):

```bash
cd NexTurn/microservices
./test_services.sh
```

**Expected output:**
```
🧪 NexTurn Microservices Testing Script
========================================
Checking if services are running...
✓ All services are running

Testing: User Signup
✓ PASSED (Status: 201)

Testing: User Login
✓ PASSED (Status: 200)

Testing: Verify JWT Token
✓ PASSED (Status: 200)

Testing: Create Business
✓ PASSED (Status: 201)

Testing: Get All Businesses
✓ PASSED (Status: 200)

Testing: Join Queue
✓ PASSED (Status: 201)

Testing: Get Ticket Details
✓ PASSED (Status: 200)

==========================================
Test Summary
==========================================
Passed: 14
Failed: 0

🎉 All tests passed!
```

### **Manual Tests**

#### **1. Sign Up a User**
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

#### **2. Login**
```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

**Save the token from the response!** You'll need it for the next steps.

#### **3. Create a Business**
```bash
curl -X POST http://localhost:5002/api/businesses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "My Café",
    "description": "Best coffee in town",
    "category": "Café",
    "address": "123 Main St"
  }'
```

Replace `YOUR_TOKEN_HERE` with the actual token from step 2.

---

## 📊 View Logs

### **View All Logs**
```bash
docker-compose logs -f
```

Press `Ctrl+C` to stop following logs.

### **View Specific Service Logs**
```bash
# Auth Service logs
docker-compose logs -f auth-service

# Business Service logs
docker-compose logs -f business-service

# Queue Service logs
docker-compose logs -f queue-service
```

---

## 🛑 Stop Services

### **Option 1: Stop (Keep Data)**
In the terminal where services are running, press `Ctrl+C`, then:
```bash
docker-compose stop
```

### **Option 2: Stop and Remove Containers**
```bash
docker-compose down
```

### **Option 3: Stop and Delete Everything (Including Data)**
```bash
docker-compose down -v
```

**⚠️ Warning:** Option 3 will delete all database data!

---

## 🔄 Restart Services

### **Start Stopped Services**
```bash
docker-compose start
```

### **Restart Running Services**
```bash
docker-compose restart
```

### **Rebuild and Restart (After Code Changes)**
```bash
docker-compose up --build
```

---

## 🐛 Troubleshooting

### **Problem: Services won't start**

#### **1. Check if ports are already in use**

**Windows:**
```bash
netstat -ano | findstr :5001
netstat -ano | findstr :5002
netstat -ano | findstr :5003
```

**Mac/Linux:**
```bash
lsof -i :5001
lsof -i :5002
lsof -i :5003
```

**Solution:** Stop the program using those ports, or change ports in `docker-compose.yml`

#### **2. Check if Docker Desktop is running**

Look for Docker icon in system tray (Windows) or menu bar (Mac).

**Solution:** Start Docker Desktop and wait for it to fully start.

#### **3. Docker daemon not responding**

```bash
docker ps
```

If this fails, restart Docker Desktop.

---

### **Problem: "Cannot connect to Docker daemon"**

**Solution:**
1. Open Docker Desktop
2. Wait for it to fully start (icon should be stable, not animated)
3. Try again

---

### **Problem: Services can't find each other**

**Example error:** `Connection refused` when Business Service calls Queue Service

**Solution:**
```bash
docker-compose down
docker-compose up --build
```

This recreates the network.

---

### **Problem: Changes not appearing**

After modifying code, changes don't show up.

**Solution:**
```bash
docker-compose down
docker-compose up --build --force-recreate
```

This forces rebuild of images.

---

### **Problem: Database not persisting**

Data disappears after restart.

**Solution:**
```bash
# Check volumes
docker volume ls

# Should see volumes for each service
docker-compose down
docker-compose up --build
```

---

### **Problem: Out of disk space**

**Clean up old containers and images:**
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything (CAREFUL!)
docker system prune -a
```

---

## 📋 Common Commands Cheat Sheet

| What You Want | Command |
|---------------|---------|
| Start services | `docker-compose up --build` |
| Start in background | `docker-compose up -d` |
| Stop services | `docker-compose stop` or `Ctrl+C` |
| Stop and remove | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| View specific service logs | `docker-compose logs -f auth-service` |
| Check status | `docker-compose ps` |
| Restart services | `docker-compose restart` |
| Rebuild images | `docker-compose up --build` |
| Run tests | `./test_services.sh` |
| Enter a container | `docker-compose exec auth-service bash` |

---

## 🎓 Next Steps

After successfully running the services:

1. ✅ Run the automated tests: `./test_services.sh`
2. ✅ Try the API endpoints with Postman or cURL
3. ✅ Check the logs to see how services communicate
4. ✅ Read the [README.md](README.md) for detailed API documentation
5. ✅ Try deploying to Kubernetes with `./deploy.sh`

---

## 🆘 Still Having Issues?

If you're still having problems:

1. **Check Docker Desktop is running** - Look for the icon in system tray/menu bar
2. **Restart Docker Desktop** - Sometimes it just needs a restart
3. **Check the logs** - Run `docker-compose logs -f` to see error messages
4. **Clean slate** - Run `docker-compose down -v && docker-compose up --build`
5. **Check disk space** - Make sure you have at least 5GB free

---

## ✨ Success!

If you see all services running and tests passing, you're all set! 🎉

**You now have 3 microservices running:**
- 🔐 Authentication Service on port 5001
- 🏢 Business Service on port 5002
- 📋 Queue Service on port 5003

**Happy coding!**
