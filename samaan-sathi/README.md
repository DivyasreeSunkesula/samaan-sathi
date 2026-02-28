# Samaan Sathi AI - Complete AWS Deployment

<div align="center">

![Samaan Sathi AI](https://img.shields.io/badge/AI-Powered-blue)
![AWS](https://img.shields.io/badge/AWS-Serverless-orange)
![Python](https://img.shields.io/badge/Python-3.11-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**AI-powered retail companion for small shop owners in India**

[Features](#features) • [Architecture](#architecture) • [Quick Start](#quick-start) • [Documentation](#documentation)

</div>

---

## 🎯 Overview

Samaan Sathi AI is a complete, production-ready serverless application that empowers small kirana and MSME shop owners with AI-powered insights for inventory management, pricing optimization, demand forecasting, and credit (udhaar) tracking.

### The Problem

Small shop owners in India face:
- ❌ No demand forecasting → overstocking and stock-outs
- ❌ Blind pricing → copying competitors without understanding demand
- ❌ High inventory wastage → expired and dead stock
- ❌ Untracked udhaar → money stuck with customers
- ❌ No access to analytics → unlike organized retail

### The Solution

✅ **AI-powered demand forecasting** (7-14 days)  
✅ **Smart pricing recommendations** based on demand elasticity  
✅ **Automated inventory alerts** for low stock and expiry  
✅ **Kaatha/Udhaar management** with risk scoring  
✅ **OCR bill processing** using AWS Textract  
✅ **Natural language recommendations** via Amazon Bedrock  

---

## 🏗️ Architecture

This application uses a **serverless, event-driven architecture** on AWS:

### Core Services

| Service | Purpose |
|---------|---------|
| **API Gateway** | RESTful API endpoints with Cognito authorization |
| **Lambda** | 8 serverless functions for business logic |
| **Bedrock** | Claude 3 for AI recommendations and explanations |
| **SageMaker** | ML models for demand forecasting |
| **Textract** | OCR for bill/receipt processing |
| **RDS PostgreSQL** | Transactional data (sales, forecasts, alerts) |
| **DynamoDB** | Real-time data (inventory, sessions, udhaar) |
| **S3** | Data lake, bills storage, ML models |
| **ElastiCache Redis** | API response caching |
| **Cognito** | User authentication and authorization |
| **CloudWatch** | Monitoring, logging, and alarms |

### Architecture Diagram

```
Mobile/Web App → API Gateway → Lambda Functions → AI/ML Services
                                      ↓
                              RDS + DynamoDB + S3
                                      ↓
                              CloudWatch Monitoring
```

See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for detailed architecture documentation.

---

## ✨ Features

### 1. 📊 Demand Forecasting
- 7-14 day demand predictions per item
- Seasonality and festival detection
- Confidence scores and recommendations
- Historical trend analysis

### 2. 💰 Pricing Recommendations
- AI-powered price optimization
- Margin analysis and suggestions
- Competitive pricing insights
- Impact predictions

### 3. 📦 Inventory Management
- Real-time stock tracking
- Low stock alerts
- Expiry date monitoring
- Category-based organization
- Dead stock identification

### 4. 💳 Kaatha/Udhaar Tracking
- Customer-wise credit ledger
- Payment recording
- Overdue alerts
- Risk scoring (0-1 scale)
- Cash flow insights

### 5. 📸 OCR Processing
- Bill/receipt image processing
- Automatic data extraction
- Structured data output
- Confidence scoring

### 6. 🤖 AI Recommendations
- Natural language insights
- Context-aware suggestions
- Multi-category recommendations
- Priority-based alerts

### 7. 🔔 Smart Alerts
- Out of stock warnings
- Low stock notifications
- Expiry alerts
- Overdue udhaar reminders
- High-risk customer flags

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required tools
- AWS Account with admin access
- AWS CLI v2+ configured
- Node.js 18+
- Python 3.11+
- AWS CDK CLI: npm install -g aws-cdk
- PostgreSQL client (psql)
```

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd samaan-sathi

# 2. Install dependencies
npm run install-all

# 3. Configure environment
cp .env.example .env
# Edit .env with your AWS account details

# 4. Deploy infrastructure
./scripts/deploy.sh dev

# 5. Initialize database
./scripts/init-database.sh dev

# 6. Enable Bedrock models
# Go to AWS Console → Bedrock → Model access
# Enable: Claude 3 Sonnet, Claude 3 Haiku
```

### Verify Deployment

```bash
# Get API URL
aws cloudformation describe-stacks \
  --stack-name SamaanSathi-API-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text

# Test API
curl https://your-api-url/health
```

---

## 📁 Project Structure

```
samaan-sathi/
├── infrastructure/              # AWS CDK infrastructure code
│   ├── bin/app.ts              # CDK app entry point
│   ├── lib/                    # Stack definitions
│   │   ├── network-stack.ts    # VPC and networking
│   │   ├── auth-stack.ts       # Cognito authentication
│   │   ├── storage-stack.ts    # S3 buckets
│   │   ├── database-stack.ts   # RDS and DynamoDB
│   │   ├── ml-stack.ts         # SageMaker infrastructure
│   │   ├── compute-stack.ts    # Lambda functions
│   │   ├── api-stack.ts        # API Gateway
│   │   └── monitoring-stack.ts # CloudWatch dashboards
│   └── package.json
│
├── backend/                     # Lambda functions
│   ├── functions/
│   │   ├── auth/               # Authentication handler
│   │   ├── inventory/          # Inventory management
│   │   ├── ocr/                # OCR processing
│   │   ├── forecast/           # Demand forecasting
│   │   ├── pricing/            # Pricing recommendations
│   │   ├── udhaar/             # Credit tracking
│   │   ├── recommendations/    # AI recommendations
│   │   └── alerts/             # Alert generation
│   ├── layers/                 # Lambda layers
│   └── requirements.txt        # Python dependencies
│
├── database/                    # Database schemas
│   └── schema.sql              # PostgreSQL schema
│
├── scripts/                     # Deployment scripts
│   ├── deploy.sh               # Main deployment script
│   ├── init-database.sh        # Database initialization
│   └── cleanup.sh              # Resource cleanup
│
├── docs/                        # Documentation
│   ├── DEPLOYMENT.md           # Deployment guide
│   ├── API.md                  # API documentation
│   └── ARCHITECTURE.md         # Architecture details
│
├── .env.example                # Environment template
├── .gitignore
├── package.json
└── README.md
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DEPLOYMENT.md](./docs/DEPLOYMENT.md) | Complete deployment guide with troubleshooting |
| [API.md](./docs/API.md) | Full API reference with examples |
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Detailed architecture documentation |

---

## 🔧 Configuration

### Environment Variables

```env
# AWS Configuration
AWS_REGION=ap-south-1
AWS_ACCOUNT_ID=your-account-id
ENVIRONMENT=dev

# Bedrock Models
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_HAIKU_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Feature Flags
ENABLE_ML_FORECASTING=true
ENABLE_BEDROCK_RECOMMENDATIONS=true
ENABLE_OCR_PROCESSING=true
```

### AWS Services Configuration

All infrastructure is defined as code using AWS CDK. Modify stack files in `infrastructure/lib/` to customize:
- VPC and networking
- Database sizing
- Lambda memory/timeout
- API Gateway throttling
- CloudWatch alarms

---

## 🧪 Testing

### API Testing

```bash
# Register user
curl -X POST https://your-api-url/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test123!","email":"test@example.com","phone":"+919876543210","fullName":"Test User"}'

# Login
curl -X POST https://your-api-url/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test123!"}'

# Add inventory item
curl -X POST https://your-api-url/inventory \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"itemId":"item-001","name":"Rice 1kg","quantity":50,"costPrice":40,"sellingPrice":50}'

# Get recommendations
curl https://your-api-url/recommendations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

See [API.md](./docs/API.md) for complete API documentation.

---

## 📊 Monitoring

### CloudWatch Dashboard

Access the monitoring dashboard:
```
AWS Console → CloudWatch → Dashboards → SamaanSathi-Monitoring
```

**Metrics tracked:**
- API request count and latency
- Lambda invocations and errors
- Database CPU and connections
- DynamoDB throttling
- Cache hit rates

### Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/samaan-sathi-inventory --follow

# View API Gateway logs
aws logs tail /aws/apigateway/SamaanSathi-API --follow
```

### Alarms

Automatic alarms for:
- Lambda errors > 5 in 5 minutes
- API 5XX errors > 10 in 5 minutes
- Database CPU > 80%
- DynamoDB throttling

---

## 💰 Cost Estimation

### Monthly Costs (Approximate)

| Environment | Traffic | Estimated Cost |
|-------------|---------|----------------|
| Development | Low | $60-100 |
| Production | Low (100 users) | $150-300 |
| Production | Medium (1000 users) | $500-800 |
| Production | High (10000 users) | $1500-2500 |

**Cost breakdown:**
- Lambda: $5-50 (based on invocations)
- RDS: $30-100 (instance size)
- DynamoDB: $5-50 (on-demand)
- S3: $5-20 (storage + requests)
- Bedrock: $10-200 (usage-based)
- Other services: $10-30

### Cost Optimization Tips

1. Use on-demand pricing for variable workloads
2. Enable S3 Intelligent Tiering
3. Configure CloudWatch log retention (7 days for dev)
4. Use Lambda provisioned concurrency only for critical functions
5. Optimize Lambda memory allocation

---

## 🔒 Security

### Best Practices Implemented

✅ **Network Security**
- VPC with private subnets
- Security groups with least privilege
- VPC endpoints for AWS services

✅ **Data Security**
- Encryption at rest (all services)
- Encryption in transit (TLS 1.2+)
- Secrets Manager for credentials
- No hardcoded secrets

✅ **Application Security**
- Input validation
- SQL injection prevention
- CORS configuration
- Rate limiting
- JWT authentication

✅ **Compliance**
- Data residency (India region)
- Audit logging (CloudTrail)
- Backup and retention policies

---

## 🚧 Roadmap

- [ ] Mobile app (React Native)
- [ ] Multi-shop support
- [ ] Supplier management
- [ ] Payment gateway integration
- [ ] Advanced analytics dashboard
- [ ] WhatsApp notifications
- [ ] Voice interface (Alexa/Google)
- [ ] Multi-language UI

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- AWS for serverless infrastructure
- Anthropic for Claude AI models
- Open source community

---

## 📞 Support

For issues and questions:
- 📧 Email: support@samaansathi.ai
- 📝 GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- 📚 Documentation: [docs/](./docs/)

---

<div align="center">

**Built with ❤️ for small shop owners in India**

[⬆ Back to top](#samaan-sathi-ai---complete-aws-deployment)

</div>
