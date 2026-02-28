# Samaan Sathi AI - Architecture Documentation

## System Overview

Samaan Sathi AI is a serverless, AI-powered retail companion built on AWS. The architecture follows microservices patterns with event-driven workflows and leverages managed AWS services for scalability and reliability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Mobile App   │  │  Web App     │  │  POS System  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                    API Gateway Layer                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Amazon API Gateway (REST API)                             │  │
│  │  - Authentication (Cognito Authorizer)                     │  │
│  │  - Rate Limiting & Throttling                              │  │
│  │  - Request/Response Transformation                         │  │
│  └────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                   Compute Layer (Lambda)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   Auth   │  │Inventory │  │   OCR    │  │ Forecast │        │
│  │ Handler  │  │ Handler  │  │ Handler  │  │ Handler  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Pricing  │  │  Udhaar  │  │Recommend │  │  Alerts  │        │
│  │ Handler  │  │ Handler  │  │ Handler  │  │ Handler  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└───────────────────────────────────────────────────────────────────┘
          │                  │                  │
          ├──────────────────┼──────────────────┤
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼─────────────────┐
│         │      AI/ML Services Layer           │                  │
│  ┌──────▼──────┐  ┌────────▼──────┐  ┌───────▼──────┐          │
│  │   Bedrock   │  │  SageMaker    │  │  Textract    │          │
│  │   Claude    │  │  Endpoints    │  │     OCR      │          │
│  │  (AI Recs)  │  │ (Forecasting) │  │              │          │
│  └─────────────┘  └───────────────┘  └──────────────┘          │
└───────────────────────────────────────────────────────────────────┘
          │                  │                  │
          ├──────────────────┼──────────────────┤
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼─────────────────┐
│         │       Data Layer                    │                  │
│  ┌──────▼──────┐  ┌────────▼──────┐  ┌───────▼──────┐          │
│  │     RDS     │  │   DynamoDB    │  │      S3      │          │
│  │ PostgreSQL  │  │  - Inventory  │  │  - Raw Data  │          │
│  │ - Sales     │  │  - Sessions   │  │  - Bills     │          │
│  │ - Forecasts │  │  - Udhaar     │  │  - Models    │          │
│  └─────────────┘  └───────────────┘  └──────────────┘          │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ElastiCache Redis (Caching Layer)                      │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│              Monitoring & Security Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │CloudWatch│  │  X-Ray   │  │ Cognito  │  │ Secrets  │        │
│  │  Logs    │  │ Tracing  │  │   Auth   │  │ Manager  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└───────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Gateway Layer

**Purpose**: Single entry point for all client requests

**Features**:
- RESTful API endpoints
- Cognito-based authentication
- Request validation and transformation
- Rate limiting (100 req/sec, burst 200)
- CORS configuration
- API key management for external integrations

**Endpoints**:
- `/auth/*` - Authentication (public)
- `/inventory/*` - Inventory management (protected)
- `/ocr/*` - OCR processing (protected)
- `/forecast/*` - Demand forecasting (protected)
- `/pricing/*` - Pricing recommendations (protected)
- `/udhaar/*` - Credit management (protected)
- `/recommendations/*` - AI recommendations (protected)
- `/alerts/*` - Alerts and notifications (protected)

### 2. Compute Layer (AWS Lambda)

**Purpose**: Serverless business logic execution

**Functions**:

1. **Auth Handler**
   - User registration and login
   - Token management
   - Cognito integration

2. **Inventory Handler**
   - CRUD operations for inventory
   - Stock level tracking
   - Category management

3. **OCR Handler**
   - Bill/receipt image processing
   - Textract integration
   - Data extraction and structuring

4. **Forecast Handler**
   - Demand prediction (7-14 days)
   - Historical data analysis
   - SageMaker endpoint invocation

5. **Pricing Handler**
   - Price optimization
   - Margin analysis
   - Competitive pricing suggestions

6. **Udhaar Handler**
   - Credit tracking
   - Payment recording
   - Risk scoring

7. **Recommendations Handler**
   - AI-powered insights
   - Bedrock Claude integration
   - Context-aware suggestions

8. **Alerts Handler**
   - Alert generation
   - Notification management
   - Priority-based sorting

**Configuration**:
- Runtime: Python 3.11
- Memory: 256MB - 1024MB
- Timeout: 30-60 seconds
- VPC: Private subnets for database access
- IAM: Least privilege roles

### 3. AI/ML Services Layer

#### Amazon Bedrock
**Purpose**: Generative AI for recommendations and explanations

**Models Used**:
- Claude 3 Sonnet: Complex reasoning and recommendations
- Claude 3 Haiku: Fast responses for simple queries

**Use Cases**:
- Generate human-readable recommendations
- Explain pricing strategies
- Answer custom queries
- Extract structured data from OCR text

#### Amazon SageMaker
**Purpose**: ML model training and inference

**Models**:
- Demand Forecasting: Time series prediction
- Price Optimization: Regression models
- Customer Risk Scoring: Classification models

**Infrastructure**:
- Training: On-demand instances
- Inference: Real-time endpoints
- Model Registry: Versioned models

#### Amazon Textract
**Purpose**: OCR for bill and receipt processing

**Features**:
- Text extraction
- Table detection
- Form field extraction
- Expense analysis

### 4. Data Layer

#### Amazon RDS (PostgreSQL)
**Purpose**: Relational data storage

**Tables**:
- `shops` - Shop information
- `sales_transactions` - Sales records
- `sales_items` - Line items
- `forecasts` - Prediction results
- `pricing_recommendations` - Price suggestions
- `alerts` - Alert history
- `ocr_logs` - OCR processing logs

**Configuration**:
- Instance: t3.small (production: t3.medium+)
- Storage: 20GB (auto-scaling to 100GB)
- Backups: 7-day retention
- Multi-AZ: Disabled (dev), Enabled (prod)

#### Amazon DynamoDB
**Purpose**: NoSQL for high-velocity data

**Tables**:

1. **Inventory Table**
   - Partition Key: `shopId`
   - Sort Key: `itemId`
   - GSI: `CategoryIndex` (shopId, category)
   - Use: Real-time inventory tracking

2. **Sessions Table**
   - Partition Key: `sessionId`
   - TTL: Enabled
   - Use: User session management

3. **Udhaar Table**
   - Partition Key: `shopId`
   - Sort Key: `customerId`
   - GSI: `OverdueIndex` (shopId, dueDate)
   - Use: Credit tracking

**Configuration**:
- Billing: On-demand
- Encryption: AWS managed
- Point-in-time recovery: Enabled

#### Amazon S3
**Purpose**: Object storage

**Buckets**:

1. **Data Bucket**
   - Raw sales data (CSV)
   - Processed datasets
   - Analytics results
   - Lifecycle: Archive to Glacier after 90 days

2. **Bills Bucket**
   - Bill/receipt images
   - OCR results
   - Lifecycle: Delete after 365 days

3. **Models Bucket**
   - ML model artifacts
   - Training data
   - Versioning: Enabled

#### Amazon ElastiCache (Redis)
**Purpose**: Caching layer

**Use Cases**:
- API response caching
- Session storage
- Frequently accessed data
- Rate limiting counters

**Configuration**:
- Node type: cache.t3.micro
- Cluster mode: Disabled
- Encryption: In-transit and at-rest

### 5. Security Layer

#### Amazon Cognito
**Purpose**: User authentication and authorization

**Features**:
- User pools for authentication
- JWT token generation
- MFA support
- Custom attributes (shopId, shopName)
- Password policies

#### AWS Secrets Manager
**Purpose**: Secure credential storage

**Secrets**:
- Database credentials
- API keys
- Third-party service tokens

#### IAM Roles and Policies
**Purpose**: Access control

**Roles**:
- Lambda execution roles
- SageMaker execution roles
- API Gateway invocation roles

**Policies**:
- Least privilege access
- Resource-based policies
- Service control policies

### 6. Monitoring Layer

#### Amazon CloudWatch
**Purpose**: Logging and monitoring

**Features**:
- Lambda function logs
- API Gateway logs
- Custom metrics
- Dashboards
- Alarms

**Metrics Tracked**:
- API request count
- Lambda invocations
- Error rates
- Latency
- Database connections

#### AWS X-Ray
**Purpose**: Distributed tracing

**Features**:
- Request tracing
- Service map
- Performance analysis
- Error detection

## Data Flow Patterns

### 1. Inventory Update Flow

```
Mobile App → API Gateway → Inventory Lambda → DynamoDB
                                            ↓
                                      CloudWatch Logs
```

### 2. OCR Processing Flow

```
Mobile App → API Gateway → OCR Lambda → Textract
                              ↓
                          S3 (Bills)
                              ↓
                          Bedrock (Structure)
                              ↓
                          DynamoDB (Save)
```

### 3. Forecast Generation Flow

```
Forecast Lambda → RDS (Historical Data)
       ↓
   SageMaker Endpoint
       ↓
   RDS (Save Forecast)
       ↓
   Return to Client
```

### 4. Recommendation Flow

```
Recommendations Lambda → DynamoDB (Inventory)
                       → DynamoDB (Udhaar)
                       → Bedrock Claude
                       → Return Insights
```

## Scalability Considerations

### Horizontal Scaling
- Lambda: Automatic concurrency scaling
- DynamoDB: On-demand capacity
- API Gateway: Automatic scaling

### Vertical Scaling
- RDS: Instance size upgrades
- ElastiCache: Node type upgrades
- Lambda: Memory allocation

### Caching Strategy
- API responses: 5-minute TTL
- Inventory data: 1-minute TTL
- Forecasts: 1-hour TTL
- Recommendations: 30-minute TTL

## Security Best Practices

1. **Network Security**
   - VPC with private subnets
   - Security groups
   - NACLs
   - VPC endpoints for AWS services

2. **Data Security**
   - Encryption at rest (all services)
   - Encryption in transit (TLS 1.2+)
   - Secrets Manager for credentials
   - IAM roles (no hardcoded credentials)

3. **Application Security**
   - Input validation
   - SQL injection prevention
   - XSS protection
   - CORS configuration
   - Rate limiting

4. **Compliance**
   - Data residency (India region)
   - Audit logging (CloudTrail)
   - Access logging
   - Backup and retention policies

## Disaster Recovery

### RTO/RPO Targets
- RTO: 4 hours
- RPO: 1 hour

### Backup Strategy
- RDS: Automated daily backups (7-day retention)
- DynamoDB: Point-in-time recovery
- S3: Versioning enabled
- Infrastructure: CDK code in Git

### Recovery Procedures
1. Database: Restore from snapshot
2. DynamoDB: Restore from backup
3. S3: Restore from versions
4. Infrastructure: Redeploy with CDK

## Cost Optimization

### Strategies
1. Use on-demand pricing for variable workloads
2. Reserved instances for predictable workloads
3. S3 Intelligent Tiering
4. Lambda memory optimization
5. DynamoDB on-demand mode
6. CloudWatch log retention policies

### Estimated Costs (Monthly)
- **Development**: $60-100
- **Production (Low Traffic)**: $150-300
- **Production (High Traffic)**: $500-1000

## Performance Optimization

### Latency Targets
- API response: < 500ms (p95)
- OCR processing: < 5s
- Forecast generation: < 10s
- Recommendations: < 2s

### Optimization Techniques
1. Lambda warm-up (provisioned concurrency)
2. Database connection pooling
3. Query optimization
4. Caching strategy
5. Async processing for heavy tasks
6. CDN for static content

## Future Enhancements

1. **Multi-region deployment**
2. **GraphQL API**
3. **Real-time notifications (WebSocket)**
4. **Mobile offline support**
5. **Advanced analytics dashboard**
6. **Integration with payment gateways**
7. **Supplier management**
8. **Multi-shop support**
