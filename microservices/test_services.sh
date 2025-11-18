#!/bin/bash

# NexTurn Microservices Testing Script

echo "🧪 NexTurn Microservices Testing Script"
echo "========================================"

BASE_URL_AUTH="http://localhost:5001"
BASE_URL_BUSINESS="http://localhost:5002"
BASE_URL_QUEUE="http://localhost:5003"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local expected_status=$4
    local description=$5
    local token=$6

    echo ""
    echo "Testing: $description"

    if [ -z "$token" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$url" -H "Content-Type: application/json" -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$url" -H "Content-Type: application/json" -H "Authorization: Bearer $token" -d "$data")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (Status: $http_code)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        echo -e "${RED}✗ FAILED${NC} (Expected: $expected_status, Got: $http_code)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo "$body"
    fi
}

# Check if services are running
echo ""
echo "Checking if services are running..."

if ! curl -s "$BASE_URL_AUTH/auth/health" > /dev/null; then
    echo -e "${RED}✗ Auth service is not running at $BASE_URL_AUTH${NC}"
    exit 1
fi

if ! curl -s "$BASE_URL_BUSINESS/api/health" > /dev/null; then
    echo -e "${RED}✗ Business service is not running at $BASE_URL_BUSINESS${NC}"
    exit 1
fi

if ! curl -s "$BASE_URL_QUEUE/api/health" > /dev/null; then
    echo -e "${RED}✗ Queue service is not running at $BASE_URL_QUEUE${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All services are running${NC}"

# Generate random email to avoid conflicts
RANDOM_EMAIL="testuser$RANDOM@example.com"

echo ""
echo "=========================================="
echo "Authentication Service Tests"
echo "=========================================="

# Test 1: Sign up
test_endpoint "POST" "$BASE_URL_AUTH/auth/signup" \
    "{\"full_name\":\"Test User\",\"email\":\"$RANDOM_EMAIL\",\"password\":\"password123\",\"confirm_password\":\"password123\",\"organization\":\"Test Org\"}" \
    201 "User Signup"

# Test 2: Login
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL_AUTH/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$RANDOM_EMAIL\",\"password\":\"password123\"}")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.token')

test_endpoint "POST" "$BASE_URL_AUTH/auth/login" \
    "{\"email\":\"$RANDOM_EMAIL\",\"password\":\"password123\"}" \
    200 "User Login"

# Test 3: Verify token
test_endpoint "GET" "$BASE_URL_AUTH/auth/verify" \
    "" 200 "Verify JWT Token" "$TOKEN"

# Test 4: Get profile
test_endpoint "GET" "$BASE_URL_AUTH/auth/profile" \
    "" 200 "Get User Profile" "$TOKEN"

echo ""
echo "=========================================="
echo "Business Service Tests"
echo "=========================================="

# Test 5: Create business
BUSINESS_RESPONSE=$(curl -s -X POST "$BASE_URL_BUSINESS/api/businesses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"name":"Test Café","description":"A test café","category":"Café","address":"123 Test St"}')

BUSINESS_ID=$(echo $BUSINESS_RESPONSE | jq -r '.data.business_id')

test_endpoint "POST" "$BASE_URL_BUSINESS/api/businesses" \
    "{\"name\":\"Test Café\",\"description\":\"A test café\",\"category\":\"Café\",\"address\":\"123 Test St\"}" \
    201 "Create Business" "$TOKEN"

# Test 6: Get all businesses
test_endpoint "GET" "$BASE_URL_BUSINESS/api/businesses" \
    "" 200 "Get All Businesses"

# Test 7: Get business by ID
test_endpoint "GET" "$BASE_URL_BUSINESS/api/businesses/$BUSINESS_ID" \
    "" 200 "Get Business by ID"

# Test 8: Get my businesses
test_endpoint "GET" "$BASE_URL_BUSINESS/api/businesses/my-businesses" \
    "" 200 "Get My Businesses" "$TOKEN"

echo ""
echo "=========================================="
echo "Queue Service Tests"
echo "=========================================="

# Wait a bit for default queue to be created
sleep 2

# Test 9: Get queues for business
QUEUES_RESPONSE=$(curl -s "$BASE_URL_QUEUE/api/queues/business/$BUSINESS_ID")
QUEUE_ID=$(echo $QUEUES_RESPONSE | jq -r '.data.queues[0].id')

test_endpoint "GET" "$BASE_URL_QUEUE/api/queues/business/$BUSINESS_ID" \
    "" 200 "Get Business Queues"

# Test 10: Join queue
JOIN_RESPONSE=$(curl -s -X POST "$BASE_URL_QUEUE/api/queues/$QUEUE_ID/join" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN")

TICKET_ID=$(echo $JOIN_RESPONSE | jq -r '.data.ticket_id')

test_endpoint "POST" "$BASE_URL_QUEUE/api/queues/$QUEUE_ID/join" \
    "" 201 "Join Queue" "$TOKEN"

# Test 11: Get ticket details
test_endpoint "GET" "$BASE_URL_QUEUE/api/tickets/$TICKET_ID" \
    "" 200 "Get Ticket Details" "$TOKEN"

# Test 12: Get my active ticket
test_endpoint "GET" "$BASE_URL_QUEUE/api/tickets/my-active" \
    "" 200 "Get My Active Ticket" "$TOKEN"

# Test 13: Get queue details
test_endpoint "GET" "$BASE_URL_QUEUE/api/queues/$QUEUE_ID" \
    "" 200 "Get Queue Details"

# Test 14: Get my history
test_endpoint "GET" "$BASE_URL_QUEUE/api/tickets/my-history" \
    "" 200 "Get My Queue History" "$TOKEN"

# Print summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo "Total: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed${NC}"
    exit 1
fi
