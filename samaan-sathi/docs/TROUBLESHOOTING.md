# Troubleshooting Guide

Common issues and solutions for Samaan Sathi AI deployment.

## Deployment Issues

### Issue: CDK Bootstrap Failed

**Error:**
```
This stack uses assets, so the toolkit stack must be deployed to the environment
```

**Solution:**
```bash
# Bootstrap CDK for your account and region
cdk bootstrap aws://YOUR_ACCOUNT_ID/ap-south-1
```

### Issue: Lambda Function Timeout

**Error:**
```
Task timed out after 30.00 seconds
```

**Solution:**
1. Increase timeout in `infrastructure/lib/compute-stack.ts`:
```typescript
timeout: cdk.Duration.seconds(60),
```

2. Increase memory (often helps with performance):
```typescript
memorySize: 1024,
```

### Issue: Database Connection Failed

**Error:**
```
could not connect to server: Connection timed out
```

**Solution:**
1. Check Lambda is in correct VPC subnets
2. Verify security group allows Lambda → RDS connection
3. Check RDS is in AVAILABLE state:
```bash
aws rds describe-db-instances --db-instance-identifier samaan-sathi-db
```

### Issue: Bedrock Access Denied

**Error:**
```
AccessDeniedException: You don't have access to the model
```

**Solution:**
1. Go to AWS Console → Bedrock → Model access
2. Enable these models:
   - Claude 3 Sonnet
   - Claude 3 Haiku
3. Wait 2-3 minutes for access to propagate

### Issue: Textract Access Denied

**Error:**
```
AccessDeniedException: User is not authorized to perform: textract:AnalyzeExpense
```

**Solution:**
Add Textract permissions to Lambda role in `compute-stack.ts`:
```typescript
lambdaRole.addToPolicy(
  new iam.PolicyStatement({
    effect: iam.Effect.ALLOW,
    actions: ['textract:*'],
    resources: ['*'],
  })
);
```

## Runtime Issues

### Issue: Cognito User Registration Failed

**Error:**
```
InvalidPasswordException: Password did not conform with policy
```

**Solution:**
Password must meet these requirements:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (optional but recommended)

Example format: `[YourPass123!]`

### Issue: DynamoDB Item Not Found

**Error:**
```
Item not found
```

**Solution:**
1. Verify table name in environment variables
2. Check partition key and sort key match:
```bash
aws dynamodb get-item \
  --table-name samaan-sathi-inventory \
  --key '{"shopId":{"S":"default-shop"},"itemId":{"S":"item-001"}}'
```

### Issue: S3 Access Denied

**Error:**
```
AccessDenied: Access Denied
```

**Solution:**
1. Check Lambda has S3 permissions
2. Verify bucket name is correct
3. Check bucket policy:
```bash
aws s3api get-bucket-policy --bucket samaan-sathi-data-YOUR_ACCOUNT_ID
```

## API Issues

### Issue: 401 Unauthorized

**Error:**
```json
{"error": "Unauthorized"}
```

**Solution:**
1. Verify JWT token is valid and not expired
2. Check Authorization header format:
```
Authorization: Bearer eyJraWQiOiJ...
```
3. Token expires in 1 hour - get new token via login

### Issue: 403 Forbidden

**Error:**
```json
{"message": "Forbidden"}
```

**Solution:**
1. Check Cognito authorizer is configured correctly
2. Verify user pool ID matches
3. Check user has required permissions

### Issue: 500 Internal Server Error

**Error:**
```json
{"error": "Internal server error"}
```

**Solution:**
1. Check CloudWatch logs:
```bash
aws logs tail /aws/lambda/samaan-sathi-inventory --follow
```
2. Look for Python exceptions
3. Check environment variables are set correctly

## Database Issues

### Issue: PostgreSQL Connection Pool Exhausted

**Error:**
```
FATAL: remaining connection slots are reserved
```

**Solution:**
1. Increase max_connections in RDS parameter group
2. Implement connection pooling in Lambda
3. Use RDS Proxy for connection management

### Issue: DynamoDB Throttling

**Error:**
```
ProvisionedThroughputExceededException
```

**Solution:**
1. Tables use on-demand billing by default
2. Check for hot partitions
3. Review access patterns

## Performance Issues

### Issue: Slow API Response

**Symptoms:**
- API responses > 2 seconds
- Lambda cold starts

**Solution:**
1. Enable provisioned concurrency for critical functions:
```typescript
const version = func.currentVersion;
const alias = new lambda.Alias(this, 'Alias', {
  aliasName: 'prod',
  version,
  provisionedConcurrentExecutions: 2,
});
```

2. Implement caching in ElastiCache
3. Optimize database queries

### Issue: High Costs

**Symptoms:**
- Unexpected AWS bill
- High Lambda invocations

**Solution:**
1. Check CloudWatch metrics for usage
2. Implement API Gateway caching
3. Review Lambda memory allocation
4. Use Cost Explorer to identify expensive services

## Monitoring Issues

### Issue: No Logs in CloudWatch

**Solution:**
1. Check Lambda execution role has CloudWatch permissions
2. Verify log group exists:
```bash
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/samaan-sathi
```

### Issue: Alarms Not Triggering

**Solution:**
1. Check SNS topic subscription is confirmed
2. Verify alarm threshold and evaluation periods
3. Check metric data is being published

## Data Issues

### Issue: OCR Extraction Inaccurate

**Solution:**
1. Ensure image quality is good (min 300 DPI)
2. Image should be clear and well-lit
3. Use JPEG or PNG format
4. Try different Textract API (AnalyzeDocument vs AnalyzeExpense)

### Issue: Forecast Accuracy Low

**Solution:**
1. Need minimum 30 days of historical data
2. Check for data quality issues
3. Retrain model with more data
4. Adjust forecast parameters

## Security Issues

### Issue: Secrets Not Found

**Error:**
```
ResourceNotFoundException: Secrets Manager can't find the specified secret
```

**Solution:**
1. Check secret exists:
```bash
aws secretsmanager list-secrets
```
2. Verify secret ARN in environment variables
3. Check Lambda has secretsmanager:GetSecretValue permission

### Issue: VPC Endpoint Connection Failed

**Solution:**
1. Check VPC endpoints are created for:
   - S3
   - DynamoDB
   - Secrets Manager
2. Verify route tables
3. Check security groups

## Cleanup Issues

### Issue: Stack Deletion Failed

**Error:**
```
Resource cannot be deleted: DeletionPolicy is Retain
```

**Solution:**
1. Some resources (RDS, DynamoDB) have RETAIN policy
2. Manually delete from AWS Console
3. Or modify stack to use DESTROY policy (not recommended for production)

### Issue: S3 Bucket Not Empty

**Error:**
```
The bucket you tried to delete is not empty
```

**Solution:**
```bash
# Empty bucket before deletion
aws s3 rm s3://samaan-sathi-data-YOUR_ACCOUNT_ID --recursive
```

## Getting Help

### Check Logs

```bash
# Lambda logs
aws logs tail /aws/lambda/FUNCTION_NAME --follow

# API Gateway logs
aws logs tail /aws/apigateway/SamaanSathi-API --follow

# RDS logs
aws rds describe-db-log-files --db-instance-identifier samaan-sathi-db
```

### Check Resource Status

```bash
# CloudFormation stacks
aws cloudformation describe-stacks --stack-name SamaanSathi-API-dev

# Lambda functions
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `samaan-sathi`)]'

# DynamoDB tables
aws dynamodb list-tables

# RDS instances
aws rds describe-db-instances
```

### Enable Debug Logging

Add to Lambda environment variables:
```bash
aws lambda update-function-configuration \
  --function-name samaan-sathi-inventory \
  --environment Variables={LOG_LEVEL=DEBUG}
```

### Contact Support

If issues persist:
1. Check AWS Service Health Dashboard
2. Review AWS Support cases
3. Post in AWS forums
4. Contact AWS Support (if you have a support plan)

## Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request body format |
| 401 | Unauthorized | Verify JWT token |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Verify resource exists |
| 429 | Too Many Requests | Implement backoff/retry |
| 500 | Internal Server Error | Check Lambda logs |
| 502 | Bad Gateway | Check Lambda timeout |
| 503 | Service Unavailable | Check service limits |
| 504 | Gateway Timeout | Increase timeout |
