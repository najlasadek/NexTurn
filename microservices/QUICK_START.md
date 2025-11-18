# 🚀 NexTurn Microservices - Quick Start Guide

## ⚡ Get Started in 5 Minutes

### Prerequisites
- Docker Desktop installed and running
- OR Python 3.9+ for local development

**📖 For detailed step-by-step instructions with troubleshooting, see [HOW_TO_RUN.md](HOW_TO_RUN.md)**

---

## Option 1: Docker Compose (Recommended - Easiest!)

### Step 1: Navigate to microservices directory
```bash
cd NexTurn/microservices
```

### Step 2: Start all services
```bash
docker-compose up --build
```

### Step 3: Wait for services to start
You'll see:
```
✓ auth-service started on port 5001
✓ business-service started on port 5002
✓ queue-service started on port 5003
```

### Step 4: Test the services
```bash
# In a new terminal
./test_services.sh
```

**That's it! All services are running!** 🎉

---

## Option 2: Run Locally (No Docker)

### Step 1: Install dependencies and run Auth Service
```bash
cd auth-service
pip install -r requirements.txt
python app/app.py
```

### Step 2: In a NEW terminal, run Business Service
```bash
cd business-service
pip install -r requirements.txt
python app/app.py
```

### Step 3: In a NEW terminal, run Queue Service
```bash
cd queue-service
pip install -r requirements.txt
python app/app.py
```

---

## 🧪 Quick Test

### 1. Sign Up
```bash
curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "confirm_password": "password123"
  }'
```

### 2. Login (Save the token!)
```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Create a Business (Replace YOUR_TOKEN with token from step 2)
```bash
curl -X POST http://localhost:5002/api/businesses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My Café",
    "description": "Best coffee in town",
    "category": "Café",
    "address": "123 Main St"
  }'
```

### 4. Get All Businesses
```bash
curl http://localhost:5002/api/businesses
```

---

## 🎯 Access Services

| Service | URL | Health Check |
|---------|-----|--------------|
| Auth | http://localhost:5001 | http://localhost:5001/auth/health |
| Business | http://localhost:5002 | http://localhost:5002/api/health |
| Queue | http://localhost:5003 | http://localhost:5003/api/health |

---

## 🛑 Stop Services

### Docker Compose
```bash
docker-compose down
```

### Local Development
Press `Ctrl+C` in each terminal

---

## 📚 Next Steps

1. Read [README.md](README.md) for detailed documentation
2. Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for architecture overview
3. Try Kubernetes deployment with `./deploy.sh`

---

## 🆘 Troubleshooting

**Problem:** Port already in use
**Solution:** Stop other services or change ports in docker-compose.yml

**Problem:** Docker not starting
**Solution:** Make sure Docker Desktop is running

**Problem:** Services can't connect
**Solution:** Ensure all services are in the same network (docker-compose handles this)

---

## ✅ Verify Everything Works

Run the automated test suite:
```bash
./test_services.sh
```

You should see:
```
✓ All tests passed!
Passed: 14
Failed: 0
```

---

**Happy Coding! 🎉**
