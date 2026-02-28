# Deploy Samaan Sathi AI to AWS - Step by Step

## 🚀 Quick Deployment Guide

Follow these steps exactly to deploy to AWS.

---

## Prerequisites Check

Before starting, verify you have:

```bash
# Check AWS CLI
aws --version
# Should show: aws-cli/2.x.x or higher

# Check AWS credentials
aws sts get-caller-identity
# Should show your AWS account ID

# Check Node.js
node --version
# Should show: v18.x.x or higher

# Check Python
python3 --version
# Should show: Python 3.11.x or higher

# Check CDK
cdk --version
# Should show: 2.x.x or higher
# If not installed: npm install -g aws-cdk
```

---

## Step 1: Navigate to Project

```bash
cd samaan-sathi
```

---

## Step 2: Install Infrastructure Dependencies

```bash
cd infrastructure
npm install
```

**Expected output:** Dependencies installed successfully

---

## Step 3: Build TypeScript

```bash
npm run build
```

**Expected output:** Compiled successfully

---

## Step 4: Verify CDK Synthesis

```bash
npx cdk synth
```

**Expected output:** CloudFormation templates generated for all 8 stacks

---

## Step 5: Bootstrap CDK (First Time Only)

```bash
# Get your AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Bootstrap CDK
npx cdk bootstrap aws://$AWS_ACCOUNT_ID/ap-south-1
```

**Expected output:** Bootstrap stack deployed successfully

**Note:** Only run this once per account/region combination.

---

## Step 6: Build Lambda Layers

```bash
cd ..
mkdir -p backend/layers/dependencies/python
pip install -r backend/requirements.txt -t backend/layers/dependencies/python/
```

**Expected output:** All Python packages installed

---

## Step 7: Deploy All Stacks

```bash
cd infrastructure

# Deploy all stacks (takes ~20 minutes)
npx cdk deploy --all --require-approval never
```

**Expected output:**
```
✅ SamaanSathi-Network-dev
✅ SamaanSathi-Auth-dev
✅ SamaanSathi-Storage-dev
✅ SamaanSathi-Database-dev
✅ SamaanSathi-ML-dev
✅ SamaanSathi-Compute-dev
✅ SamaanSathi-API-dev
✅ SamaanSathi-Monitoring-dev
```

**Save the outputs!** You'll see important information like:
- API URL
- User Pool ID
- Database endpoint

---

## Step 8: Initialize Database

```bash
cd ..

# Get database credentials
export DB_SECRET_ARN=$(aws cloudformation describe-stacks \
  --stack-name SamaanSathi-Database-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`DatabaseSecretArn`].OutputValue' \
  --output text)

export DB_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name SamaanSathi-Database-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
  --output text)

# Get credentials from Secrets Manager
aws secretsmanager get-secret-value --secret-id $DB_SECRET_ARN

# Apply database schema
# Note: You'll need psql installed
# Install: 
#   Ubuntu/Debian: sudo apt-get install postgresql-client
#   macOS: brew install postgresql
#   Windows: Download from postgresql.org

# Run the init script
chmod +x scripts/init-database.sh
./scripts/init-database.sh dev
```

**Expected output:** Database schema applied successfully

---

## Step 9: Enable Bedrock Models

**Manual step required:**

1. Go to AWS Console: https://console.aws.amazon.com/bedrock/
2. Click "Model access" in the left menu
3. Click "Manage model access"
4. Enable these models:
   - ✅ Claude 3 Sonnet
   - ✅ Claude 3 Haiku
5. Click "Save changes"
6. Wait 2-3 minutes for access to be granted

---

## Step 10: Get API URL

```bash
export API_URL=$(aws cloudformation describe-stacks \
  --stack-name SamaanSathi-API-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

echo "Your API URL: $API_URL"
```

**Save this URL!** You'll need it for testing.

---

## Step 11: Test Deployment

```bash
# Make test script executable
chmod +x scripts/test-api.sh

# Run tests
./scripts/test-api.sh dev
```

**Expected output:** All tests pass with HTTP 200/201 responses

---

## Step 12: Subscribe to Alerts (Optional)

```bash
export ALERT_TOPIC_ARN=$(aws cloudformation describe-stacks \
  --stack-name SamaanSathi-Monitoring-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`AlertTopicArn`].OutputValue' \
  --output text)

# Subscribe your email
aws sns subscribe \
  --topic-arn $ALERT_TOPIC_ARN \
  --protocol email \
  --notification-endpoint your-email@example.com

# Check your email and confirm subscription
```

---

## Verification Checklist

After deployment, verify:

- [ ] All 8 CloudFormation stacks show "CREATE_COMPLETE"
- [ ] API Gateway URL is accessible
- [ ] Lambda functions are created (8 functions)
- [ ] RDS database is available
- [ ] DynamoDB tables are created (3 tables)
- [ ] S3 buckets are created (3 buckets)
- [ ] Cognito user pool is created
- [ ] CloudWatch dashboard is visible
- [ ] Database schema is applied
- [ ] Bedrock models are enabled
- [ ] Test API calls succeed

---

## Quick Test Commands

### Test 1: Register User

```bash
curl -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!",
    "email": "test@example.com",
    "phone": "+919876543210",
    "fullName": "Test User",
    "shopName": "Test Shop"
  }'
```

### Test 2: Login

```bash
curl -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

**Save the accessToken from the response!**

### Test 3: Add Inventory

```bash
export ACCESS_TOKEN="your-token-here"

curl -X POST "$API_URL/inventory" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "itemId": "item-001",
    "name": "Rice 1kg",
    "category": "groceries",
    "quantity": 50,
    "costPrice": 40,
    "sellingPrice": 50,
    "minStockLevel": 10
  }'
```

### Test 4: Get Recommendations

```bash
curl "$API_URL/recommendations" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## Troubleshooting

### Issue: CDK Bootstrap Failed

```bash
# Ensure you have admin permissions
aws iam get-user

# Try bootstrap again with explicit account/region
npx cdk bootstrap aws://YOUR_ACCOUNT_ID/ap-south-1
```

### Issue: Lambda Deployment Failed

```bash
# Check Lambda layers directory exists
ls -la backend/layers/dependencies/python/

# Rebuild if needed
rm -rf backend/layers/dependencies/python/
pip install -r backend/requirements.txt -t backend/layers/dependencies/python/
```

### Issue: Database Connection Failed

```bash
# Check RDS status
aws rds describe-db-instances \
  --db-instance-identifier $(aws rds describe-db-instances \
    --query 'DBInstances[?contains(DBInstanceIdentifier, `samaan`)].DBInstanceIdentifier' \
    --output text)

# Ensure status is "available"
```

### Issue: Bedrock Access Denied

- Go to AWS Console → Bedrock → Model access
- Ensure models are enabled and status is "Access granted"
- Wait 2-3 minutes after enabling

---

## View Deployed Resources

### CloudFormation Stacks

```bash
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE \
  --query 'StackSummaries[?contains(StackName, `SamaanSathi`)].StackName'
```

### Lambda Functions

```bash
aws lambda list-functions \
  --query 'Functions[?contains(FunctionName, `samaan-sathi`)].FunctionName'
```

### DynamoDB Tables

```bash
aws dynamodb list-tables \
  --query 'TableNames[?contains(@, `samaan-sathi`)]'
```

### S3 Buckets

```bash
aws s3 ls | grep samaan-sathi
```

### API Gateway

```bash
aws apigateway get-rest-apis \
  --query 'items[?contains(name, `Samaan`)].{Name:name,ID:id}'
```

---

## CloudWatch Dashboard

View monitoring dashboard:

```bash
echo "https://console.aws.amazon.com/cloudwatch/home?region=ap-south-1#dashboards:name=SamaanSathi-Monitoring"
```

---

## Cost Monitoring

Set up cost alert:

```bash
aws budgets create-budget \
  --account-id $AWS_ACCOUNT_ID \
  --budget file://budget.json
```

Create `budget.json`:
```json
{
  "BudgetName": "SamaanSathi-Monthly",
  "BudgetLimit": {
    "Amount": "100",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

---

## Cleanup (When Needed)

To remove all resources:

```bash
chmod +x scripts/cleanup.sh
./scripts/cleanup.sh dev
```

**Warning:** This will delete all data!

---

## Next Steps After Deployment

1. ✅ Test all API endpoints
2. ✅ Create test users and data
3. ✅ Monitor CloudWatch dashboard
4. ✅ Review costs in Cost Explorer
5. ✅ Set up CI/CD pipeline (optional)
6. ✅ Configure custom domain (optional)
7. ✅ Enable CloudFront CDN (optional)
8. ✅ Set up backup policies
9. ✅ Perform security audit
10. ✅ Load testing

---

## Support

If you encounter issues:

1. Check [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)
2. Review CloudWatch logs
3. Check AWS Service Health Dashboard
4. Review deployment outputs

---

## Success! 🎉

If all steps completed successfully, you now have:

✅ Fully deployed Samaan Sathi AI on AWS
✅ 8 CloudFormation stacks
✅ 8 Lambda functions
✅ Complete API with 20+ endpoints
✅ AI-powered recommendations
✅ OCR bill processing
✅ Demand forecasting
✅ Credit tracking
✅ Monitoring and alerts

**Your API is live at:** `$API_URL`

**Start using it!** 🚀
