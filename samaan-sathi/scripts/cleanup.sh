#!/bin/bash

# Samaan Sathi AI Cleanup Script
# WARNING: This will delete all resources and data

set -e

ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-ap-south-1}

echo "⚠️  WARNING: This will delete all Samaan Sathi AI resources!"
echo "Environment: $ENVIRONMENT"
echo "Region: $AWS_REGION"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo "🗑️  Starting cleanup..."

# Empty S3 buckets before deletion
echo "📦 Emptying S3 buckets..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws s3 rm s3://samaan-sathi-data-$ACCOUNT_ID --recursive || true
aws s3 rm s3://samaan-sathi-bills-$ACCOUNT_ID --recursive || true
aws s3 rm s3://samaan-sathi-models-$ACCOUNT_ID --recursive || true

# Destroy CDK stacks
echo "🔥 Destroying CDK stacks..."
cd infrastructure

npx cdk destroy SamaanSathi-Monitoring-$ENVIRONMENT --force
npx cdk destroy SamaanSathi-API-$ENVIRONMENT --force
npx cdk destroy SamaanSathi-Compute-$ENVIRONMENT --force
npx cdk destroy SamaanSathi-ML-$ENVIRONMENT --force
npx cdk destroy SamaanSathi-Database-$ENVIRONMENT --force
npx cdk destroy SamaanSathi-Storage-$ENVIRONMENT --force
npx cdk destroy SamaanSathi-Auth-$ENVIRONMENT --force
npx cdk destroy SamaanSathi-Network-$ENVIRONMENT --force

cd ..

echo "✅ Cleanup completed!"
echo ""
echo "Note: Some resources may be retained based on RemovalPolicy settings."
echo "Check AWS Console to verify all resources are deleted."
