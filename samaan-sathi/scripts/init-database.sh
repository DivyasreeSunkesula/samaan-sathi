#!/bin/bash

# Initialize RDS PostgreSQL database with schema

set -e

echo "🗄️  Initializing database..."

ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-ap-south-1}

# Get database endpoint and credentials
DB_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name SamaanSathi-Database-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
    --output text \
    --region $AWS_REGION)

SECRET_ARN=$(aws cloudformation describe-stacks \
    --stack-name SamaanSathi-Database-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`DatabaseSecretArn`].OutputValue' \
    --output text \
    --region $AWS_REGION)

# Get database credentials from Secrets Manager
DB_CREDENTIALS=$(aws secretsmanager get-secret-value \
    --secret-id $SECRET_ARN \
    --query SecretString \
    --output text \
    --region $AWS_REGION)

DB_USERNAME=$(echo $DB_CREDENTIALS | jq -r '.username')
DB_PASSWORD=$(echo $DB_CREDENTIALS | jq -r '.password')

echo "📡 Database endpoint: $DB_ENDPOINT"
echo "👤 Username: $DB_USERNAME"

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo "❌ psql is not installed. Please install PostgreSQL client."
    echo "   Ubuntu/Debian: sudo apt-get install postgresql-client"
    echo "   macOS: brew install postgresql"
    exit 1
fi

# Run schema script
echo "📝 Applying database schema..."
PGPASSWORD=$DB_PASSWORD psql \
    -h $DB_ENDPOINT \
    -U $DB_USERNAME \
    -d samaansathi \
    -f database/schema.sql

echo "✅ Database initialized successfully!"
