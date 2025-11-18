# NexTurn Microservices Testing Guide

## 🧪 Complete Testing Procedures

### Prerequisites
All services must be running:
```bash
cd NexTurn/microservices
docker-compose ps
```

You should see all 4 services with status "Up".

---

## Method 1: Web Interface Testing (Recommended for Demo)

### 1. **Test User Registration Flow**

**Steps:**
1. Open browser: http://localhost:5000
2. Click "Sign Up" or navigate to http://localhost:5000/signup
3. Fill in the form:
   - Full Name: `John Doe`
   - Email: `john@example.com`
   - Organization: `Test Corp`
   - Password: `password123`
   - Confirm Password: `password123`
4. Click "Create Account"

**Expected Result:**
- ✅ Account created successfully message
- ✅ Redirects to login page
- ✅ Data stored in auth-service database

**Backend Services Involved:**
- Frontend Gateway → Auth Service (5001)

---

### 2. **Test User Login Flow**

**Steps:**
1. Navigate to http://localhost:5000/login
2. Enter credentials:
   - Email: `john@example.com`
   - Password: `password123`
3. Click "Log In"

**Expected Result:**
- ✅ Login successful
- ✅ JWT token generated and stored
- ✅ Redirects to dashboard/home

**Backend Services Involved:**
- Frontend Gateway → Auth Service (5001)

---

### 3. **Test Business Registration**

**Steps:**
1. After logging in, navigate to http://localhost:5000/register-business
2. Fill in business details:
   - Business Name: `Joe's Café`
   - Category: `Restaurant`
   - Address: `123 Main Street`
   - Phone: `555-0100`
   - Description: `Best coffee in town`
3. Click "Register Business"

**Expected Result:**
- ✅ Business created successfully
- ✅ Default queue created automatically
- ✅ Redirects to business dashboard

**Backend Services Involved:**
- Frontend Gateway → Auth Service (JWT verification)
- Frontend Gateway → Business Service (5002)
- Business Service → Queue Service (5003) - creates default queue

---

### 4. **Test Browse Businesses**

**Steps:**
1. Navigate to http://localhost:5000/businesses
2. View list of all registered businesses

**Expected Result:**
- ✅ Shows "Joe's Café" and any other businesses
- ✅ Can click on a business to see details

**Backend Services Involved:**
- Frontend Gateway → Business Service (5002)

---

### 5. **Test Queue Management**

**Steps:**
1. Navigate to http://localhost:5000/business-dashboard
2. View your business queues
3. Create a new queue or select existing queue
4. Manage queue settings

**Expected Result:**
- ✅ Can see all queues for your business
- ✅ Can update queue settings
- ✅ Can see waiting customers

**Backend Services Involved:**
- Frontend Gateway → Queue Service (5003)

---

### 6. **Test Join Queue**

**Steps:**
1. Open a different browser (or incognito window)
2. Login as a different user
3. Navigate to http://localhost:5000/businesses
4. Click on "Joe's Café"
5. Click "Join Queue"

**Expected Result:**
- ✅ Ticket generated with UUID
- ✅ Position in queue shown
- ✅ Estimated wait time displayed

**Backend Services Involved:**
- Frontend Gateway → Queue Service (5003)

---

## Method 2: API Testing with cURL (Backend Testing)

Test each microservice directly to verify the APIs work independently.

### Test Auth Service (Port 5001)

**1. Health Check:**
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

**2. User Signup:**
```bash
curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Smith",
    "email": "jane@example.com",
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
    "user_id": 2
  }
}
```

**3. User Login:**
```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@example.com",
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
      "id": 2,
      "email": "jane@example.com",
      "full_name": "Jane Smith"
    }
  }
}
```

**Save the token for subsequent requests!**

---

### Test Business Service (Port 5002)

**1. Health Check:**
```bash
curl http://localhost:5002/api/health
```

**2. Create Business (requires JWT token):**
```bash
# Replace YOUR_TOKEN with the token from login response
curl -X POST http://localhost:5002/api/businesses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Pizza Palace",
    "category": "Restaurant",
    "address": "456 Oak Avenue"
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

**3. List All Businesses:**
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
        "name": "Joe's Café",
        "category": "Restaurant",
        "address": "123 Main Street"
      },
      {
        "id": 2,
        "name": "Pizza Palace",
        "category": "Restaurant",
        "address": "456 Oak Avenue"
      }
    ]
  }
}
```

**4. Get My Businesses (requires JWT):**
```bash
curl http://localhost:5002/api/businesses/my-businesses \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Test Queue Service (Port 5003)

**1. Health Check:**
```bash
curl http://localhost:5003/api/health
```

**2. Create Queue (requires JWT):**
```bash
curl -X POST http://localhost:5003/api/queues \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "business_id": 1,
    "name": "Main Queue",
    "avg_service_time": 5
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Queue created successfully",
  "data": {
    "queue_id": 1
  }
}
```

**3. Join Queue (requires JWT):**
```bash
curl -X POST http://localhost:5003/api/queues/1/join \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
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

**4. Get Ticket Status:**
```bash
curl http://localhost:5003/api/tickets/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**5. Serve Next Customer (business owner only):**
```bash
curl -X POST http://localhost:5003/api/queues/1/serve-next \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{}'
```

**6. Get Business Queues:**
```bash
curl http://localhost:5003/api/queues/business/1
```

---

## Method 3: Test via Frontend Gateway (Port 5000)

The frontend gateway proxies all API calls. Test the same endpoints through port 5000:

**Example - Signup via Gateway:**
```bash
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Bob Builder",
    "email": "bob@example.com",
    "password": "password123",
    "confirm_password": "password123"
  }'
```

**This tests the complete flow:**
1. Request hits Frontend Gateway (5000)
2. Gateway proxies to Auth Service (5001)
3. Auth Service processes and responds
4. Gateway returns response to client

---

## Method 4: Automated Test Script

Create a test script to verify all services:

```bash
#!/bin/bash
# test_all_services.sh

echo "🧪 Testing NexTurn Microservices"
echo "================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Test Auth Service
echo -e "\n1️⃣ Testing Auth Service..."
HEALTH=$(curl -s http://localhost:5001/auth/health | grep -o '"status":"healthy"')
if [ ! -z "$HEALTH" ]; then
    echo -e "${GREEN}✅ Auth Service: HEALTHY${NC}"
else
    echo -e "${RED}❌ Auth Service: FAILED${NC}"
fi

# Test Business Service
echo -e "\n2️⃣ Testing Business Service..."
HEALTH=$(curl -s http://localhost:5002/api/health | grep -o '"status":"healthy"')
if [ ! -z "$HEALTH" ]; then
    echo -e "${GREEN}✅ Business Service: HEALTHY${NC}"
else
    echo -e "${RED}❌ Business Service: FAILED${NC}"
fi

# Test Queue Service
echo -e "\n3️⃣ Testing Queue Service..."
HEALTH=$(curl -s http://localhost:5003/api/health | grep -o '"status":"healthy"')
if [ ! -z "$HEALTH" ]; then
    echo -e "${GREEN}✅ Queue Service: HEALTHY${NC}"
else
    echo -e "${RED}❌ Queue Service: FAILED${NC}"
fi

# Test Frontend Gateway
echo -e "\n4️⃣ Testing Frontend Gateway..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)
if [ "$STATUS" == "200" ]; then
    echo -e "${GREEN}✅ Frontend Gateway: HEALTHY${NC}"
else
    echo -e "${RED}❌ Frontend Gateway: FAILED (HTTP $STATUS)${NC}"
fi

# Test Signup
echo -e "\n5️⃣ Testing User Signup..."
SIGNUP=$(curl -s -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test'$(date +%s)'@test.com","password":"test123","confirm_password":"test123"}')
SUCCESS=$(echo $SIGNUP | grep -o '"success":true')
if [ ! -z "$SUCCESS" ]; then
    echo -e "${GREEN}✅ Signup: SUCCESS${NC}"
else
    echo -e "${RED}❌ Signup: FAILED${NC}"
fi

echo -e "\n✅ Testing Complete!"
```

---

## Expected Test Results Summary

| Test | Endpoint | Expected Status | Service(s) Involved |
|------|----------|----------------|---------------------|
| Auth Health | GET /auth/health | 200 OK | Auth |
| Business Health | GET /api/health | 200 OK | Business |
| Queue Health | GET /api/health | 200 OK | Queue |
| Frontend Home | GET / | 200 OK | Frontend |
| User Signup | POST /auth/signup | 201 Created | Frontend → Auth |
| User Login | POST /auth/login | 200 OK | Frontend → Auth |
| Create Business | POST /api/businesses | 201 Created | Frontend → Business |
| List Businesses | GET /api/businesses | 200 OK | Frontend → Business |
| Create Queue | POST /api/queues | 201 Created | Frontend → Queue |
| Join Queue | POST /api/queues/:id/join | 200 OK | Frontend → Queue |
| Get Ticket | GET /api/tickets/:id | 200 OK | Frontend → Queue |

---

## Troubleshooting Common Issues

### Issue 1: Service Returns 503 (Service Unavailable)
**Cause:** Backend service is down
**Solution:**
```bash
docker-compose ps
docker-compose logs [service-name]
docker-compose restart [service-name]
```

### Issue 2: 401 Unauthorized on Protected Routes
**Cause:** Missing or invalid JWT token
**Solution:** Login first and use the returned token

### Issue 3: Database Errors
**Cause:** Database not initialized
**Solution:**
```bash
docker-compose down -v  # Remove volumes
docker-compose up --build  # Rebuild and restart
```

### Issue 4: CORS Errors in Browser
**Cause:** CORS not properly configured
**Solution:** Already configured in frontend gateway, should work automatically

---

## Performance Testing

Test service response times:

```bash
# Test Auth Service response time
time curl -s http://localhost:5001/auth/health > /dev/null

# Test Business Service response time
time curl -s http://localhost:5002/api/health > /dev/null

# Test Queue Service response time
time curl -s http://localhost:5003/api/health > /dev/null
```

---

## Load Testing (Optional)

Use Apache Bench to test under load:

```bash
# Test 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:5000/

# Test signup endpoint
ab -n 50 -c 5 -p signup.json -T 'application/json' http://localhost:5000/auth/signup
```

---

## Monitoring Service Logs

**View logs for all services:**
```bash
docker-compose logs -f
```

**View logs for specific service:**
```bash
docker-compose logs -f frontend-service
docker-compose logs -f auth-service
docker-compose logs -f business-service
docker-compose logs -f queue-service
```

**View last 50 lines:**
```bash
docker-compose logs --tail=50 auth-service
```

---

## Success Criteria

✅ All services return 200/201 on health checks
✅ User can signup, login, and receive JWT token
✅ Authenticated user can create businesses
✅ Anyone can view business listings
✅ Authenticated user can create queues
✅ Authenticated user can join queues and receive tickets
✅ Business owner can serve next customer
✅ All database operations persist correctly
✅ Services communicate correctly through gateway

---

## Next Steps

After testing confirms everything works:
1. Deploy to Kubernetes with Minikube
2. Set up monitoring with Prometheus/Grafana
3. Implement remaining services (Feedback, Analytics, Notification)
4. Add integration tests
5. Set up CI/CD pipeline
