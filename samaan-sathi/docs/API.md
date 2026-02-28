# Samaan Sathi AI - API Documentation

Complete API reference for Samaan Sathi AI retail companion.

## Base URL

```
https://your-api-id.execute-api.ap-south-1.amazonaws.com/prod
```

## Authentication

All endpoints (except `/auth/*`) require JWT authentication.

### Headers

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Endpoints

### Authentication

#### Register User

```http
POST /auth/register
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string",
  "phone": "string",
  "fullName": "string",
  "shopName": "string" (optional)
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "username": "string"
}
```

#### Login

```http
POST /auth/login
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "accessToken": "string",
  "idToken": "string",
  "refreshToken": "string",
  "expiresIn": 3600
}
```

---

### Inventory Management

#### Get All Inventory Items

```http
GET /inventory?category=groceries
```

**Query Parameters:**
- `category` (optional): Filter by category

**Response:**
```json
{
  "items": [
    {
      "shopId": "string",
      "itemId": "string",
      "name": "string",
      "category": "string",
      "quantity": 50,
      "unit": "kg",
      "costPrice": 40,
      "sellingPrice": 50,
      "minStockLevel": 10,
      "expiryDate": "2024-12-31",
      "supplier": "string",
      "lastUpdated": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

#### Get Single Item

```http
GET /inventory/{itemId}
```

**Response:**
```json
{
  "shopId": "string",
  "itemId": "string",
  "name": "Rice 1kg",
  "category": "groceries",
  "quantity": 50,
  "unit": "kg",
  "costPrice": 40,
  "sellingPrice": 50,
  "minStockLevel": 10
}
```

#### Add/Update Item

```http
POST /inventory
```

**Request Body:**
```json
{
  "itemId": "item-001",
  "name": "Rice 1kg",
  "category": "groceries",
  "quantity": 50,
  "unit": "kg",
  "costPrice": 40,
  "sellingPrice": 50,
  "minStockLevel": 10,
  "expiryDate": "2024-12-31",
  "supplier": "ABC Suppliers"
}
```

**Response:**
```json
{
  "message": "Item saved successfully",
  "item": { ... }
}
```

---

### OCR Processing

#### Process Bill/Receipt

```http
POST /ocr/process
```

**Request Body (S3):**
```json
{
  "s3Key": "bills/bill-001.jpg"
}
```

**Request Body (Base64):**
```json
{
  "imageBase64": "base64_encoded_image_string"
}
```

**Response:**
```json
{
  "rawText": "extracted text",
  "structuredData": {
    "date": "2024-01-15",
    "vendor": "ABC Store",
    "total": 450.50,
    "items": [
      {
        "name": "Rice 1kg",
        "quantity": 2,
        "price": 100
      }
    ]
  },
  "confidence": 0.92
}
```

---

### Demand Forecasting

#### Get Forecasts

```http
GET /forecast
```

**Response:**
```json
{
  "shopId": "string",
  "forecasts": [
    {
      "itemId": "item-001",
      "itemName": "Rice 1kg",
      "forecast": [
        {
          "date": "2024-01-16",
          "predictedQuantity": 12,
          "lowerBound": 10,
          "upperBound": 14
        }
      ],
      "confidence": 0.85,
      "recommendation": "Stock 50 units for next 2 weeks"
    }
  ],
  "generatedAt": "2024-01-15T10:30:00Z"
}
```

#### Generate New Forecast

```http
POST /forecast/demand
```

**Request Body:**
```json
{
  "itemIds": ["item-001", "item-002"],
  "days": 14
}
```

**Response:**
```json
{
  "shopId": "string",
  "forecasts": [ ... ],
  "generatedAt": "2024-01-15T10:30:00Z"
}
```

---

### Pricing Recommendations

#### Get Pricing Recommendations

```http
GET /pricing/recommendations
```

**Response:**
```json
{
  "shopId": "string",
  "recommendations": [
    {
      "itemId": "item-001",
      "itemName": "Rice 1kg",
      "currentPrice": 50,
      "suggestedPrice": 52,
      "currentMargin": 20,
      "suggestedMargin": 23,
      "action": "INCREASE",
      "reason": "Low margin detected. Increase price to improve profitability.",
      "confidence": 0.75
    }
  ],
  "generatedAt": "2024-01-15T10:30:00Z"
}
```

#### Optimize Pricing (AI)

```http
POST /pricing/optimize
```

**Request Body:**
```json
{
  "itemIds": ["item-001", "item-002"]
}
```

**Response:**
```json
{
  "shopId": "string",
  "optimizedPricing": [
    {
      "itemId": "item-001",
      "suggestedPrice": 52,
      "strategy": "competitive",
      "explanation": "Based on demand analysis..."
    }
  ],
  "generatedAt": "2024-01-15T10:30:00Z"
}
```

---

### Udhaar (Credit) Management

#### Get All Udhaar Records

```http
GET /udhaar?status=PENDING
```

**Query Parameters:**
- `status` (optional): PENDING, PAID, OVERDUE

**Response:**
```json
{
  "shopId": "string",
  "records": [
    {
      "customerId": "cust-001",
      "customerName": "John Doe",
      "outstandingAmount": 500,
      "status": "PENDING",
      "dueDate": "2024-02-15",
      "lastUpdated": "2024-01-15T10:30:00Z"
    }
  ],
  "summary": {
    "totalOutstanding": 5000,
    "totalCustomers": 10,
    "overdueCount": 2
  }
}
```

#### Get Customer Udhaar

```http
GET /udhaar/{customerId}
```

**Response:**
```json
{
  "customer": {
    "customerId": "cust-001",
    "customerName": "John Doe",
    "outstandingAmount": 500,
    "status": "PENDING",
    "dueDate": "2024-02-15"
  },
  "transactions": [
    {
      "transactionId": "txn-001",
      "type": "CREDIT",
      "amount": 500,
      "date": "2024-01-15T10:30:00Z",
      "items": ["Rice", "Wheat"]
    }
  ],
  "riskScore": 0.3
}
```

#### Add Udhaar Entry

```http
POST /udhaar
```

**Request Body:**
```json
{
  "customerId": "cust-001",
  "customerName": "John Doe",
  "amount": 500,
  "items": ["Rice 1kg", "Wheat 1kg"]
}
```

**Response:**
```json
{
  "message": "Udhaar added successfully",
  "record": { ... }
}
```

#### Record Payment

```http
POST /udhaar/payment
```

**Request Body:**
```json
{
  "customerId": "cust-001",
  "amount": 200
}
```

**Response:**
```json
{
  "message": "Payment recorded successfully",
  "record": {
    "outstandingAmount": 300,
    "status": "PENDING"
  }
}
```

---

### AI Recommendations

#### Get Recommendations

```http
GET /recommendations
```

**Response:**
```json
{
  "shopId": "string",
  "recommendations": [
    {
      "category": "Inventory Management",
      "title": "Restock Low Inventory Items",
      "description": "You have 5 items running low. Restock Rice, Wheat, Sugar to avoid stock-outs.",
      "priority": "HIGH",
      "expectedImpact": "Prevent lost sales due to stock-outs"
    }
  ],
  "generatedAt": "2024-01-15T10:30:00Z"
}
```

#### Generate Custom Recommendation

```http
POST /recommendations/generate
```

**Request Body:**
```json
{
  "query": "How can I improve my profit margins?",
  "context": {
    "currentMargin": 15,
    "targetMargin": 20
  }
}
```

**Response:**
```json
{
  "query": "How can I improve my profit margins?",
  "answer": "To improve your profit margins from 15% to 20%, consider: 1) Negotiate better prices with suppliers...",
  "generatedAt": "2024-01-15T10:30:00Z"
}
```

---

### Alerts

#### Get Alerts

```http
GET /alerts
```

**Response:**
```json
{
  "shopId": "string",
  "alerts": [
    {
      "type": "LOW_STOCK",
      "priority": "HIGH",
      "title": "Low Stock Warning",
      "message": "5 items are running low: Rice, Wheat, Sugar",
      "action": "Plan restocking for these items",
      "items": ["Rice 1kg", "Wheat 1kg", "Sugar 1kg"]
    },
    {
      "type": "OVERDUE_UDHAAR",
      "priority": "HIGH",
      "title": "Overdue Payments",
      "message": "₹2500 overdue from 3 customers",
      "action": "Follow up with customers for payment",
      "customers": [
        {"name": "John Doe", "amount": 500}
      ]
    }
  ],
  "count": 2,
  "generatedAt": "2024-01-15T10:30:00Z"
}
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error

---

## Rate Limiting

- Standard tier: 100 requests/second
- Burst: 200 requests
- Daily quota: 10,000 requests

---

## Pagination

For endpoints returning lists, use query parameters:

```
?limit=20&offset=0
```

---

## Webhooks (Future)

Webhook support for real-time notifications:
- Stock alerts
- Udhaar overdue
- Price changes

---

## SDKs and Client Libraries

Coming soon:
- JavaScript/TypeScript SDK
- Python SDK
- Mobile SDKs (React Native)
