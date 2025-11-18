# Direct Microservice Testing Guide

This guide shows you how to test each individual microservice directly on their respective ports.

---

## 🔍 Quick Overview

| Service | Port | Base URL | Purpose |
|---------|------|----------|---------|
| **Frontend Gateway** | 5000 | http://localhost:5000 | Web UI + API Gateway |
| **Auth Service** | 5001 | http://localhost:5001 | User authentication |
| **Business Service** | 5002 | http://localhost:5002 | Business management |
| **Queue Service** | 5003 | http://localhost:5003 | Queue & ticket management |

---

## 🧪 Testing Auth Service (Port 5001)

### 1. Health Check
```bash
curl http://localhost:5001/auth/health
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "service": "auth-service",
    "status": "healthy"
  }
}
```

### 2. User Signup
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

**Expected Response:**
```json
{
  "success": true,
  "message": "Account created successfully",
  "data": {
    "user_id": 1
  }
}
```

### 3. User Login
```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "email": "john@example.com",
      "full_name": "John Doe"
    }
  }
}
```

**💡 IMPORTANT:** Save the `token` value - you'll need it for authenticated requests!

### 4. Verify Token
```bash
# Replace YOUR_TOKEN with the token from login
curl http://localhost:5001/auth/verify \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Get User Profile
```bash
curl http://localhost:5001/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🏢 Testing Business Service (Port 5002)

### 1. Health Check
```bash
curl http://localhost:5002/api/health
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "service": "business-service",
    "status": "healthy"
  }
}
```

### 2. List All Businesses (No Auth Required)
```bash
curl http://localhost:5002/api/businesses
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "businesses": [
      {
        "id": 1,
        "name": "Test Cafe",
        "category": "Cafe",
        "address": "123 Main St",
        "owner_id": 1,
        "created_at": "2025-11-18 12:22:07"
      }
    ]
  }
}
```

### 3. Create Business (Requires JWT)
```bash
# First, get a JWT token from login (see Auth Service section)
TOKEN="your_jwt_token_here"

curl -X POST http://localhost:5002/api/businesses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Pizza Palace",
    "category": "Restaurant",
    "address": "456 Oak Avenue",
    "phone": "555-0100",
    "description": "Best pizza in town"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Business created successfully",
  "data": {
    "business_id": 2
  }
}
```

**Note:** When you create a business, a default queue is automatically created!

### 4. Get Specific Business
```bash
curl http://localhost:5002/api/businesses/1
```

### 5. Get My Businesses (Requires JWT)
```bash
curl http://localhost:5002/api/businesses/my-businesses \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Get Business Statistics
```bash
curl http://localhost:5002/api/businesses/1/stats
```

---

## 📋 Testing Queue Service (Port 5003)

### 1. Health Check
```bash
curl http://localhost:5003/api/health
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "service": "queue-service",
    "status": "healthy"
  }
}
```

### 2. Get Queues for a Business (No Auth Required)
```bash
curl http://localhost:5003/api/queues/business/1
```

**Expected Response:**
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
        "size": 0,
        "created_at": "2025-11-18 12:22:32"
      }
    ]
  }
}
```

### 3. Create a Queue (Requires JWT)
```bash
TOKEN="your_jwt_token_here"

curl -X POST http://localhost:5003/api/queues \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "business_id": 1,
    "name": "Express Queue",
    "avg_service_time": 3
  }'
```

### 4. Join a Queue (Requires JWT)
```bash
curl -X POST http://localhost:5003/api/queues/1/join \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Joined queue successfully",
  "data": {
    "ticket_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "position": 1,
    "eta": 5,
    "queue_name": "Main Queue"
  }
}
```

**💡 IMPORTANT:** Save the `ticket_id` - you'll need it to check ticket status!

### 5. Get Ticket Status
```bash
TICKET_ID="a1b2c3d4-e5f6-7890-abcd-ef1234567890"

curl http://localhost:5003/api/tickets/$TICKET_ID \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Get My Active Ticket
```bash
curl http://localhost:5003/api/tickets/my-active \
  -H "Authorization: Bearer $TOKEN"
```

### 7. Serve Next Customer (Business Owner Only)
```bash
curl -X POST http://localhost:5003/api/queues/1/serve-next \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'
```

### 8. Cancel a Ticket
```bash
curl -X POST http://localhost:5003/api/tickets/$TICKET_ID/cancel \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'
```

---

## 🌐 Browser Testing

You can also test the services directly in your browser:

### View in Browser:

1. **Auth Service Swagger/Docs:**
   - Not available (API only)
   - Use curl or Postman

2. **Business Service:**
   - List businesses: http://localhost:5002/api/businesses
   - Get business 1: http://localhost:5002/api/businesses/1

3. **Queue Service:**
   - Get queues for business 1: http://localhost:5003/api/queues/business/1
   - Get queue 1: http://localhost:5003/api/queues/1

4. **Frontend Gateway:**
   - Home: http://localhost:5000
   - Login: http://localhost:5000/login
   - Signup: http://localhost:5000/signup
   - Businesses: http://localhost:5000/businesses

---

## 🔄 Complete Testing Flow

Here's a complete workflow testing all services:

```bash
# Step 1: Create a user via Auth Service
curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@example.com","password":"test123","confirm_password":"test123"}'

# Step 2: Login to get JWT token
RESPONSE=$(curl -s -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}')

# Extract token (Linux/Mac)
TOKEN=$(echo $RESPONSE | grep -o '"token":"[^"]*' | sed 's/"token":"//')

# Or manually copy the token from the response
echo $RESPONSE

# Step 3: Create a business via Business Service
curl -X POST http://localhost:5002/api/businesses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"My Cafe","category":"Cafe","address":"123 Test St"}'

# Step 4: List businesses
curl http://localhost:5002/api/businesses

# Step 5: Get queues for the business (business_id = 1)
curl http://localhost:5003/api/queues/business/1

# Step 6: Join a queue
curl -X POST http://localhost:5003/api/queues/1/join \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'

# Step 7: Check your ticket
curl http://localhost:5003/api/tickets/my-active \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🛠️ Using Postman (Alternative to curl)

If you prefer a GUI tool:

1. **Download Postman:** https://www.postman.com/downloads/

2. **Import Collection:** Create a new collection for each service

3. **Set Variables:**
   - Create environment variable `baseUrl5001` = `http://localhost:5001`
   - Create environment variable `baseUrl5002` = `http://localhost:5002`
   - Create environment variable `baseUrl5003` = `http://localhost:5003`
   - Create environment variable `token` (will be set after login)

4. **Test Endpoints:**
   - Create requests for each endpoint
   - For authenticated requests, add header: `Authorization: Bearer {{token}}`

---

## 📊 Monitoring Service Logs

To see what's happening in each service:

```bash
# View all services
docker-compose logs -f

# View specific service
docker-compose logs -f auth-service
docker-compose logs -f business-service
docker-compose logs -f queue-service
docker-compose logs -f frontend-service

# View last 50 lines
docker-compose logs --tail=50 auth-service
```

---

## 🔍 Common Scenarios

### Scenario 1: Test Authentication Flow
```bash
# Signup
curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Alice","email":"alice@test.com","password":"pass123","confirm_password":"pass123"}'

# Login
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"pass123"}'

# Verify (use token from login)
curl http://localhost:5001/auth/verify \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Scenario 2: Test Business Creation
```bash
# Login first to get token
TOKEN="your_token_here"

# Create business
curl -X POST http://localhost:5002/api/businesses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Bob's Burgers","category":"Restaurant","address":"789 Elm St"}'

# Verify it was created
curl http://localhost:5002/api/businesses
```

### Scenario 3: Test Queue Management
```bash
# Get queues for business 1
curl http://localhost:5003/api/queues/business/1

# Join queue 1
curl -X POST http://localhost:5003/api/queues/1/join \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'

# Check your active ticket
curl http://localhost:5003/api/tickets/my-active \
  -H "Authorization: Bearer $TOKEN"
```

---

## ❌ Error Examples

### 401 Unauthorized
```json
{
  "success": false,
  "message": "Token is missing"
}
```
**Fix:** Add `Authorization: Bearer YOUR_TOKEN` header

### 422 Validation Failed
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "name": "Required",
    "category": "Required"
  }
}
```
**Fix:** Include all required fields in your request

### 404 Not Found
```json
{
  "success": false,
  "message": "Business not found"
}
```
**Fix:** Check that the resource exists (correct ID)

---

## ✅ Success Indicators

You know everything is working when:

- ✅ Health checks return 200 OK with "healthy" status
- ✅ Signup returns 201 Created with user_id
- ✅ Login returns 200 OK with JWT token
- ✅ Create business returns 201 Created with business_id
- ✅ Join queue returns 200 OK with ticket_id and position
- ✅ All GET requests return proper data structures

---

## 🎯 Quick Test Script

Create a file `test_services.sh`:

```bash
#!/bin/bash

echo "Testing NexTurn Microservices"
echo "=============================="

# Test Auth Service
echo -e "\n1. Auth Service Health:"
curl -s http://localhost:5001/auth/health | head -10

# Test Business Service
echo -e "\n2. Business Service Health:"
curl -s http://localhost:5002/api/health | head -10

# Test Queue Service
echo -e "\n3. Queue Service Health:"
curl -s http://localhost:5003/api/health | head -10

# List businesses
echo -e "\n4. List Businesses:"
curl -s http://localhost:5002/api/businesses | head -20

echo -e "\n\n✅ Basic tests complete!"
```

Run it:
```bash
chmod +x test_services.sh
./test_services.sh
```

---

## 🔗 Related Documentation

- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Comprehensive testing procedures
- [STATUS_UPDATE.md](STATUS_UPDATE.md) - Current system status and fixes
- [README.md](../README.md) - Main project documentation

---

## 💡 Tips

1. **Use jq for pretty JSON:**
   ```bash
   curl http://localhost:5002/api/businesses | jq '.'
   ```

2. **Save token to variable:**
   ```bash
   TOKEN=$(curl -s -X POST http://localhost:5001/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123"}' \
     | grep -o '"token":"[^"]*' | sed 's/"token":"//')
   ```

3. **Test with different users:**
   - Create multiple accounts to test queue positions
   - Use different tokens for business owner vs customer

4. **Monitor real-time:**
   ```bash
   # In one terminal
   docker-compose logs -f auth-service

   # In another terminal
   curl -X POST http://localhost:5001/auth/signup ...
   ```

---

**Happy Testing! 🎉**
