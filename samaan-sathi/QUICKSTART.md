# Samaan Sathi AI - Quick Start Guide

## 🚀 Deploy in 5 Minutes

### Prerequisites

Ensure you have:
- AWS Account with admin access
- AWS CLI configured (`aws configure`)
- Node.js 18+ installed
- Python 3.11+ installed
- AWS CDK installed (`npm install -g aws-cdk`)

### One-Command Deployment

```bash
cd samaan-sathi
chmod +x scripts/deploy.sh
./scripts/deploy.sh dev
```

That's it! The script will:
1. ✅ Install all dependencies
2. ✅ Build TypeScript code
3. ✅ Create Lambda layers
4. ✅ Bootstrap CDK
5. ✅ Deploy all 8 stacks (~20 minutes)
6. ✅ Display deployment info

### Post-Deployment (2 steps)

#### 1. Initialize Database

```bash
chmod +x scripts/init-database.sh
./scripts/init-database.sh dev
```

#### 2. Enable Bedrock Models

Go to: https://console.aws.amazon.com/bedrock/
- Click "Model access"
- Enable: Claude 3 Sonnet, Claude 3 Haiku
- Wait 2-3 minutes

### Test Your Deployment

```bash
chmod +x scripts/test-api.sh
./scripts/test-api.sh dev
```

### Access Your API

Your API URL will be displayed after deployment. Use it to:

**Register a user:**
```bash
curl -X POST "YOUR_API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!",
    "email": "test@example.com",
    "phone": "+919876543210",
    "fullName": "Test User"
  }'
```

**Login:**
```bash
curl -X POST "YOUR_API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

### View Monitoring Dashboard

```
https://console.aws.amazon.com/cloudwatch/home?region=ap-south-1#dashboards:name=SamaanSathi-Monitoring
```

### Cleanup (When Done)

```bash
chmod +x scripts/cleanup.sh
./scripts/cleanup.sh dev
```

---

## 📚 Full Documentation

- [Complete Deployment Guide](./DEPLOY_NOW.md)
- [API Reference](./docs/API.md)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)
- [Architecture Details](./docs/ARCHITECTURE.md)

---

## 🆘 Need Help?

Check [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) for common issues and solutions.

---

**That's it! You're ready to go! 🎉**
