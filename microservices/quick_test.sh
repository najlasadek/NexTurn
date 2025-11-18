#!/bin/bash
# Quick Test Script for NexTurn Microservices

echo "🧪 NexTurn Microservices Quick Test"
echo "===================================="

# Test all health endpoints
echo ""
echo "1️⃣ Testing Health Endpoints..."
echo "Auth Service:"
curl -s http://localhost:5001/auth/health | jq '.'

echo ""
echo "Business Service:"
curl -s http://localhost:5002/api/health | jq '.'

echo ""
echo "Queue Service:"
curl -s http://localhost:5003/api/health | jq '.'

# Test signup
echo ""
echo "2️⃣ Testing User Signup..."
TIMESTAMP=$(date +%s)
SIGNUP_RESPONSE=$(curl -s -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d "{
    \"full_name\": \"Test User $TIMESTAMP\",
    \"email\": \"test$TIMESTAMP@example.com\",
    \"password\": \"password123\",
    \"confirm_password\": \"password123\"
  }")
echo "$SIGNUP_RESPONSE" | jq '.'

# Test login
echo ""
echo "3️⃣ Testing User Login..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"test$TIMESTAMP@example.com\",
    \"password\": \"password123\"
  }")
echo "$LOGIN_RESPONSE" | jq '.'

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.token')
echo ""
echo "🔑 JWT Token: $TOKEN"

# Test create business
echo ""
echo "4️⃣ Testing Create Business..."
BUSINESS_RESPONSE=$(curl -s -X POST http://localhost:5000/api/businesses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Test Business $TIMESTAMP\",
    \"category\": \"Restaurant\",
    \"address\": \"123 Test Street\"
  }")
echo "$BUSINESS_RESPONSE" | jq '.'

BUSINESS_ID=$(echo "$BUSINESS_RESPONSE" | jq -r '.data.business_id')

# Test list businesses
echo ""
echo "5️⃣ Testing List Businesses..."
curl -s http://localhost:5000/api/businesses | jq '.'

# Test create queue
echo ""
echo "6️⃣ Testing Create Queue..."
QUEUE_RESPONSE=$(curl -s -X POST http://localhost:5000/api/queues \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"business_id\": $BUSINESS_ID,
    \"name\": \"Main Queue\",
    \"avg_service_time\": 5
  }")
echo "$QUEUE_RESPONSE" | jq '.'

QUEUE_ID=$(echo "$QUEUE_RESPONSE" | jq -r '.data.queue_id')

# Test join queue
echo ""
echo "7️⃣ Testing Join Queue..."
JOIN_RESPONSE=$(curl -s -X POST http://localhost:5000/api/queues/$QUEUE_ID/join \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}')
echo "$JOIN_RESPONSE" | jq '.'

TICKET_ID=$(echo "$JOIN_RESPONSE" | jq -r '.data.ticket_id')

# Test get ticket
echo ""
echo "8️⃣ Testing Get Ticket Status..."
curl -s http://localhost:5000/api/tickets/$TICKET_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo ""
echo "✅ All tests completed!"
echo ""
echo "Summary:"
echo "- User Created: test$TIMESTAMP@example.com"
echo "- Business Created: ID $BUSINESS_ID"
echo "- Queue Created: ID $QUEUE_ID"
echo "- Ticket Created: ID $TICKET_ID"
echo ""
echo "🌐 Open in browser: http://localhost:5000"
