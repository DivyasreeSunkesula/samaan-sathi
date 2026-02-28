#!/bin/bash

# Samaan Sathi AI Deployment Script

set -e

echo "🚀 Starting Samaan Sathi AI Deployment..."
echo ""

# Check prerequisites
echo "✓ Checking prerequisites..."
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v cdk >/dev/null 2>&1 || { echo "❌ AWS CDK is required. Install: npm install -g aws-cdk" >&2; exit 1; }

# Verify AWS credentials
echo "✓ Verifying AWS credentials..."
aws sts get-caller-identity >/dev/null 2>&1 || { echo "❌ AWS credentials not configured. Run: aws configure" >&2; exit 1; }

# Set environment
ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-ap-south-1}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "✓ Prerequisites check passed!"
echo ""
echo "📦 Environment: $ENVIRONMENT"
echo "🌍 Region: $AWS_REGION"
echo "🔑 Account: $AWS_ACCOUNT_ID"
echo ""

# Install dependencies
echo "📥 Installing infrastructure dependencies..."
cd infrastructure
npm install --silent
echo "✓ Dependencies installed"
echo ""

# Build TypeScript
echo "🔨 Building TypeScript..."
npm run build --silent
echo "✓ TypeScript compiled"
echo ""

# Build Lambda layers
echo "📦 Building Lambda layers..."
cd ..
mkdir -p backend/layers/dependencies/python
pip install -q -r backend/requirements.txt -t backend/layers/dependencies/python/
echo "✓ Lambda layers built"
echo ""

# Bootstrap CDK (if needed)
echo "🎯 Bootstrapping CDK..."
cd infrastructure
npx cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION --require-approval never 2>/dev/null || echo "✓ CDK already bootstrapped"
echo ""

# Deploy infrastructure
echo "🏗️  Deploying infrastructure (this takes ~20 minutes)..."
echo ""
npx cdk deploy --all --require-approval never

# Get stack outputs
echo ""
echo "📊 Retrieving deployment information..."
API_URL=$(aws cloudformation describe-stacks \
    --stack-name SamaanSathi-API-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text \
    --region $AWS_REGION 2>/dev/null || echo "Not available")

USER_POOL_ID=$(aws cloudformation describe-stacks \
    --stack-name SamaanSathi-Auth-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
    --output text \
    --region $AWS_REGION 2>/dev/null || echo "Not available")

DB_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name SamaanSathi-Database-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
    --output text \
    --region $AWS_REGION 2>/dev/null || echo "Not available")

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📝 Deployment Information:"
echo "  Environment:    $ENVIRONMENT"
echo "  Region:         $AWS_REGION"
echo "  API URL:        $API_URL"
echo "  User Pool ID:   $USER_POOL_ID"
echo "  DB Endpoint:    $DB_ENDPOINT"
echo ""
echo "🔗 Next Steps:"
echo ""
echo "  1. Initialize Database:"
echo "     cd .."
echo "     ./scripts/init-database.sh $ENVIRONMENT"
echo ""
echo "  2. Enable Bedrock Models:"
echo "     Go to: https://console.aws.amazon.com/bedrock/"
echo "     Enable: Claude 3 Sonnet, Claude 3 Haiku"
echo ""
echo "  3. Test API:"
echo "     ./scripts/test-api.sh $ENVIRONMENT"
echo ""
echo "  4. View Dashboard:"
echo "     https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#dashboards:name=SamaanSathi-Monitoring"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📚 Documentation:"
echo "  - API Reference:     docs/API.md"
echo "  - Troubleshooting:   docs/TROUBLESHOOTING.md"
echo "  - Architecture:      docs/ARCHITECTURE.md"
echo ""
echo "🎉 Happy coding!"
echo ""
