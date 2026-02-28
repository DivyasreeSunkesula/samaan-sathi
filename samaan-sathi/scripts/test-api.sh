#!/bin/bash

# Test API endpoints after deployment

set -e

ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-ap-south-1}

# Get API URL
API_URL=$(aws cloudformation describe-stacks \
    --stack-name SamaanSathi-API-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text \
    --region $AWS_REGION)

echo "🧪 Testing Samaan Sathi AI API"
echo "API URL: $API_URL"
echo ""

# Test 1: Register user
echo "1️⃣  Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "testuser",
        "password": "[your-password]",
        "email": "test@example.com",
        "phone": "+919876543210",
        "fullName": "Test User",
        "shopName": "Test Shop"
    }')

echo "Response: $REGISTER_RESPONSE"
echo ""

# Test 2: Login
echo "2️⃣  Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "testuser",
        "password": "[your-password]"
    }')

echo "Response: $LOGIN_RESPONSE"

# Extract access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.accessToken')

if [ "$ACCESS_TOKEN" != "null" ] && [ -n "$ACCESS_TOKEN" ]; then
    echo "✅ Login successful!"
    echo ""
    
    # Test 3: Add inventory item
    echo "3️⃣  Testing inventory creation..."
    INVENTORY_RESPONSE=$(curl -s -X POST "$API_URL/inventory" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -d '{
            "itemId": "test-item-001",
            "name": "Test Rice 1kg",
            "category": "groceries",
            "quantity": 50,
            "unit": "kg",
            "costPrice": 40,
            "sellingPrice": 50,
            "minStockLevel": 10
        }')
    
    echo "Response: $INVENTORY_RESPONSE"
    echo ""
    
    # Test 4: Get inventory
    echo "4️⃣  Testing inventory retrieval..."
    GET_INVENTORY=$(curl -s -X GET "$API_URL/inventory" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    
    echo "Response: $GET_INVENTORY"
    echo ""
    
    # Test 5: Get recommendations
    echo "5️⃣  Testing AI recommendations..."
    RECOMMENDATIONS=$(curl -s -X GET "$API_URL/recommendations" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    
    echo "Response: $RECOMMENDATIONS"
    echo ""
    
    # Test 6: Get alerts
    echo "6️⃣  Testing alerts..."
    ALERTS=$(curl -s -X GET "$API_URL/alerts" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    
    echo "Response: $ALERTS"
    echo ""
    
    echo "✅ All tests completed!"
else
    echo "❌ Login failed. Cannot proceed with authenticated tests."
fi
