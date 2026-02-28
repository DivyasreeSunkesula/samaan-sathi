# Samaan Sathi AI - Deployment Guide

Complete guide to deploy Samaan Sathi AI to AWS.

## Prerequisites

### Required Tools
- AWS CLI v2+ configured with appropriate credentials
- Node.js 18+ and npm
- Python 3.11+
- AWS CDK CLI (`npm install -g aws-cdk`)
- PostgreSQL client (psql) for database initialization
- Docker (optional, for local testing)

### AWS Account Requirements
- AWS Account with admin access
- Sufficient service limits for:
  - Lambda functions (8+)
  - RDS instances (1)
  - DynamoDB tables (3)
  - S3 buckets (3)
  - API Gateway (1)
  - Cognito User Pool (1)

### AWS Service Permissions
Ensure your IAM user/role has permissions for:
- CloudFormation
- Lambda
- API Gateway
- RDS
- DynamoDB
- S3
- Cognito
- SageMaker
- Bedrock
- Textract
- CloudWatch
- IAM (for role creation)
- Secrets Manager

## Step-by-Step Deployment

### 1. Clone and Setup

```bash
git clone <repository-url>
cd samaan-sathi

# Install all dependencies
npm run install-all
```

### 2. Configure Environment

Create `.env` file in the root directory:

```env
AWS_REGION=ap-south-1
ENVIRONMENT=dev
AWS_ACCOUNT_ID=your-account-id
```

### 3. Bootstrap CDK (First Time Only)

```bash
cd infrastructure
npx cdk bootstrap aws://YOUR_ACCOUNT_ID/ap-south-1
```

### 4. Deploy Infrastructure

```bash
# Deploy all stacks
./scripts/deploy.sh dev

# Or deploy individual stacks
cd infrastructure
npx cdk deploy SamaanSathi-Network-dev
npx cdk deploy SamaanSathi-Auth-dev
npx cdk deploy SamaanSathi-Storage-dev
npx cdk deploy SamaanSathi-Database-dev
npx cdk deploy SamaanSathi-ML-dev
npx cdk deploy SamaanSathi-Compute-dev
npx cdk deploy SamaanSathi-API-dev
npx cdk deploy SamaanSathi-Monitoring-dev
```

### 5. Initialize Database

```bash
./scripts/init-database.sh dev
```

### 6. Enable Bedrock Models

Go to AWS Console → Bedrock → Model access and enable:
- Claude 3 Sonnet
- Claude 3 Haiku

### 7. Verify Deployment

```bash
# Get API URL
aws cloudformation describe-stacks \
  --stack-name SamaanSathi-API-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text

# Test API
curl https://your-api-url/health
```

## Post-Deployment Configuration

### 1. Create Admin User

```bash
aws cognito-idp admin-create-user \
  --user-pool-id YOUR_USER_POOL_ID \
  --username admin \
  --user-attributes Name=email,Value=admin@example.com \

```

### 2. Configure CloudWatch Alarms

Alarms are automatically created for:
- Lambda errors
- API Gateway 5XX errors
- Database CPU utilization
- DynamoDB throttling

Subscribe to SNS topic for alerts:

```bash
aws sns subscribe \
  --topic-arn YOUR_ALERT_TOPIC_ARN \
  --protocol email \
  --notification-endpoint your-email@example.com
```

### 3. Upload Sample Data (Optional)

```bash
# Upload sample inventory data
aws s3 cp sample-data/inventory.csv s3://samaan-sathi-data-YOUR_ACCOUNT_ID/sample/

# Upload sample bill images
aws s3 cp sample-data/bills/ s3://samaan-sathi-bills-YOUR_ACCOUNT_ID/sample/ --recursive
```

## Testing the Deployment

### 1. Test Authentication

```bash
# Register new user
curl -X POST https://your-api-url/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "[your-username]",
    "password": "[your-password]",
    "email": "[your-email]",
    "phone": "+91XXXXXXXXXX",
    "fullName": "[Your Name]",
    "shopName": "[Your Shop]"
  }'

# Login
curl -X POST https://your-api-url/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "[your-username]",
    "password": "[your-password]"
  }'
```

### 2. Test Inventory API

```bash
# Add inventory item
curl -X POST https://your-api-url/inventory \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "itemId": "item-001",
    "name": "Rice 1kg",
    "category": "groceries",
    "quantity": 50,
    "unit": "kg",
    "costPrice": 40,
    "sellingPrice": 50,
    "minStockLevel": 10
  }'

# Get all inventory
curl https://your-api-url/inventory \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Test OCR Processing

```bash
# Process bill image
curl -X POST https://your-api-url/ocr/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "s3Key": "sample/bill-001.jpg"
  }'
```

### 4. Test Forecasting

```bash
# Generate forecast
curl -X POST https://your-api-url/forecast/demand \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "itemIds": ["item-001", "item-002"],
    "days": 14
  }'
```

### 5. Test Recommendations

```bash
# Get AI recommendations
curl https://your-api-url/recommendations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Monitoring and Logs

### CloudWatch Logs

View logs for each Lambda function:

```bash
# View inventory function logs
aws logs tail /aws/lambda/samaan-sathi-inventory --follow

# View OCR function logs
aws logs tail /aws/lambda/samaan-sathi-ocr --follow
```

### CloudWatch Dashboard

Access the monitoring dashboard:
1. Go to AWS Console → CloudWatch → Dashboards
2. Open "SamaanSathi-Monitoring"
3. View metrics for API, Lambda, and Database

### X-Ray Tracing

View distributed traces:
1. Go to AWS Console → X-Ray
2. View service map and traces
3. Analyze performance bottlenecks

## Troubleshooting

### Common Issues

#### 1. Lambda Function Timeout
- Increase timeout in `infrastructure/lib/compute-stack.ts`
- Increase memory allocation

#### 2. Database Connection Issues
- Check VPC security groups
- Verify Lambda functions are in correct subnets
- Check database credentials in Secrets Manager

#### 3. Bedrock Access Denied
- Enable model access in Bedrock console
- Verify IAM permissions for Lambda execution role

#### 4. API Gateway 403 Errors
- Check Cognito authorizer configuration
- Verify JWT token is valid
- Check API Gateway resource policies

### Debug Mode

Enable debug logging:

```bash
# Update Lambda environment variable
aws lambda update-function-configuration \
  --function-name samaan-sathi-inventory \
  --environment Variables={LOG_LEVEL=DEBUG}
```

## Scaling Considerations

### Production Recommendations

1. **Database**
   - Enable Multi-AZ deployment
   - Configure read replicas
   - Increase allocated storage

2. **Lambda**
   - Configure reserved concurrency
   - Enable provisioned concurrency for critical functions
   - Optimize memory allocation

3. **API Gateway**
   - Configure custom domain
   - Enable caching
   - Set up WAF rules

4. **DynamoDB**
   - Review and optimize GSI usage
   - Enable auto-scaling
   - Configure backups

5. **S3**
   - Enable versioning
   - Configure lifecycle policies
   - Set up cross-region replication

## Cost Optimization

### Estimated Monthly Costs (Low Traffic)

- Lambda: $5-10
- RDS (t3.small): $30-40
- DynamoDB (on-demand): $5-15
- S3: $5-10
- API Gateway: $3-5
- Bedrock: $10-50 (usage-based)
- Total: ~$60-130/month

### Cost Reduction Tips

1. Use Spot Instances for SageMaker training
2. Enable S3 Intelligent Tiering
3. Use DynamoDB on-demand for variable workloads
4. Configure CloudWatch log retention
5. Delete unused resources

## Backup and Disaster Recovery

### Automated Backups

- RDS: 7-day automated backups
- DynamoDB: Point-in-time recovery enabled
- S3: Versioning enabled

### Manual Backup

```bash
# Backup RDS
aws rds create-db-snapshot \
  --db-instance-identifier samaan-sathi-db \
  --db-snapshot-identifier samaan-sathi-backup-$(date +%Y%m%d)

# Export DynamoDB table
aws dynamodb create-backup \
  --table-name samaan-sathi-inventory \
  --backup-name inventory-backup-$(date +%Y%m%d)
```

### Disaster Recovery

1. Database: Restore from automated backup or snapshot
2. DynamoDB: Restore from backup or point-in-time
3. S3: Restore from versioned objects
4. Infrastructure: Redeploy using CDK

## Cleanup

To remove all resources:

```bash
# Destroy all stacks
cd infrastructure
npx cdk destroy --all

# Or use script
./scripts/cleanup.sh dev
```

**Warning**: This will delete all data. Ensure backups are taken before cleanup.

## Support

For issues and questions:
- Check CloudWatch Logs
- Review AWS Service Health Dashboard
- Contact AWS Support for service-specific issues
