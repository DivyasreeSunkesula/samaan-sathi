#!/bin/bash

# Samaan Sathi AI - Frontend Deployment Script
# Deploys frontend to AWS S3 + CloudFront

set -e

echo "🚀 Samaan Sathi AI - Frontend Deployment"
echo "========================================"

# Configuration
BUCKET_NAME="samaan-sathi-frontend-$(date +%s)"
REGION="ap-south-1"
FRONTEND_DIR="samaan-sathi/frontend"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ AWS CLI found${NC}"

# Get API Gateway URL
echo ""
echo "📡 Fetching API Gateway URL..."
API_URL=$(aws cloudformation describe-stacks \
    --stack-name SamaanSathi-API-dev \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text 2>/dev/null || echo "")

if [ -z "$API_URL" ]; then
    echo -e "${YELLOW}⚠️  Could not auto-detect API URL${NC}"
    echo "Please enter your API Gateway URL:"
    read -p "API URL: " API_URL
fi

echo -e "${GREEN}✓ API URL: $API_URL${NC}"

# Update config.js
echo ""
echo "📝 Updating configuration..."
cat > "$FRONTEND_DIR/config.js" << EOF
// API Configuration - Auto-generated
const CONFIG = {
    API_URL: '$API_URL',
    
    FEATURES: {
        ENABLE_AUTO_REFRESH: true,
        REFRESH_INTERVAL: 30000,
        ENABLE_NOTIFICATIONS: true,
        ENABLE_CHARTS: true,
        ENABLE_EXPORT: true
    },
    
    ENDPOINTS: {
        AUTH_REGISTER: '/auth/register',
        AUTH_LOGIN: '/auth/login',
        INVENTORY: '/inventory',
        UDHAAR: '/udhaar',
        UDHAAR_PAYMENT: '/udhaar/payment',
        FORECAST: '/forecast',
        FORECAST_DEMAND: '/forecast/demand',
        PRICING: '/pricing/recommendations',
        RECOMMENDATIONS: '/recommendations',
        ALERTS: '/alerts',
        OCR_PROCESS: '/ocr/process'
    },
    
    UI: {
        ITEMS_PER_PAGE: 20,
        TOAST_DURATION: 5000,
        ANIMATION_DURATION: 300
    }
};
EOF

echo -e "${GREEN}✓ Configuration updated${NC}"

# Create S3 bucket
echo ""
echo "🪣 Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION

echo -e "${GREEN}✓ Bucket created: $BUCKET_NAME${NC}"

# Enable static website hosting
echo ""
echo "🌐 Enabling static website hosting..."
aws s3 website s3://$BUCKET_NAME \
    --index-document index.html \
    --error-document index.html

echo -e "${GREEN}✓ Static website hosting enabled${NC}"

# Create bucket policy
echo ""
echo "🔓 Setting bucket policy..."
cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file:///tmp/bucket-policy.json

echo -e "${GREEN}✓ Bucket policy set${NC}"

# Upload files
echo ""
echo "📤 Uploading files to S3..."
aws s3 sync $FRONTEND_DIR s3://$BUCKET_NAME \
    --exclude "*.md" \
    --exclude "node_modules/*" \
    --exclude ".git/*" \
    --cache-control "max-age=86400" \
    --delete

echo -e "${GREEN}✓ Files uploaded${NC}"

# Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "🌐 Website URL: $WEBSITE_URL"
echo "🪣 S3 Bucket: $BUCKET_NAME"
echo "📡 API URL: $API_URL"
echo ""
echo "📋 Next Steps:"
echo "1. Open the website URL in your browser"
echo "2. Register a new account"
echo "3. Start using Samaan Sathi AI!"
echo ""
echo "💡 Tip: For HTTPS, set up CloudFront distribution"
echo ""

# Save deployment info
cat > "$FRONTEND_DIR/deployment-info.txt" << EOF
Deployment Information
=====================
Date: $(date)
S3 Bucket: $BUCKET_NAME
Website URL: $WEBSITE_URL
API URL: $API_URL
Region: $REGION
EOF

echo -e "${GREEN}✓ Deployment info saved to deployment-info.txt${NC}"
