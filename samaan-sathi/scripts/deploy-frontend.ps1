# Samaan Sathi AI - Frontend Deployment Script (PowerShell)
# Deploys frontend to AWS S3 + CloudFront

Write-Host "🚀 Samaan Sathi AI - Frontend Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Configuration
$BUCKET_NAME = "samaan-sathi-frontend-$(Get-Date -Format 'yyyyMMddHHmmss')"
$REGION = "ap-south-1"
$FRONTEND_DIR = "samaan-sathi/frontend"

# Check AWS CLI
try {
    aws --version | Out-Null
    Write-Host "✓ AWS CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install it first." -ForegroundColor Red
    exit 1
}

# Get API Gateway URL
Write-Host "`n📡 Fetching API Gateway URL..." -ForegroundColor Yellow
try {
    $API_URL = aws cloudformation describe-stacks `
        --stack-name SamaanSathi-API-dev `
        --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' `
        --output text 2>$null
} catch {
    $API_URL = ""
}

if ([string]::IsNullOrEmpty($API_URL)) {
    Write-Host "⚠️  Could not auto-detect API URL" -ForegroundColor Yellow
    $API_URL = Read-Host "Please enter your API Gateway URL"
}

Write-Host "✓ API URL: $API_URL" -ForegroundColor Green

# Update config.js
Write-Host "`n📝 Updating configuration..." -ForegroundColor Yellow
$configContent = @"
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
"@

$configContent | Out-File -FilePath "$FRONTEND_DIR/config.js" -Encoding UTF8
Write-Host "✓ Configuration updated" -ForegroundColor Green

# Create S3 bucket
Write-Host "`n🪣 Creating S3 bucket..." -ForegroundColor Yellow
aws s3 mb s3://$BUCKET_NAME --region $REGION
Write-Host "✓ Bucket created: $BUCKET_NAME" -ForegroundColor Green

# Enable static website hosting
Write-Host "`n🌐 Enabling static website hosting..." -ForegroundColor Yellow
aws s3 website s3://$BUCKET_NAME `
    --index-document index.html `
    --error-document index.html
Write-Host "✓ Static website hosting enabled" -ForegroundColor Green

# Create bucket policy
Write-Host "`n🔓 Setting bucket policy..." -ForegroundColor Yellow
$policyContent = @"
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
"@

$policyFile = "$env:TEMP/bucket-policy.json"
$policyContent | Out-File -FilePath $policyFile -Encoding UTF8

aws s3api put-bucket-policy `
    --bucket $BUCKET_NAME `
    --policy file:///$policyFile
Write-Host "✓ Bucket policy set" -ForegroundColor Green

# Upload files
Write-Host "`n📤 Uploading files to S3..." -ForegroundColor Yellow
aws s3 sync $FRONTEND_DIR s3://$BUCKET_NAME `
    --exclude "*.md" `
    --exclude "node_modules/*" `
    --exclude ".git/*" `
    --cache-control "max-age=86400" `
    --delete
Write-Host "✓ Files uploaded" -ForegroundColor Green

# Get website URL
$WEBSITE_URL = "http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`n🌐 Website URL: $WEBSITE_URL" -ForegroundColor White
Write-Host "🪣 S3 Bucket: $BUCKET_NAME" -ForegroundColor White
Write-Host "📡 API URL: $API_URL" -ForegroundColor White
Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open the website URL in your browser"
Write-Host "2. Register a new account"
Write-Host "3. Start using Samaan Sathi AI!"
Write-Host "`n💡 Tip: For HTTPS, set up CloudFront distribution`n" -ForegroundColor Cyan

# Save deployment info
$deploymentInfo = @"
Deployment Information
=====================
Date: $(Get-Date)
S3 Bucket: $BUCKET_NAME
Website URL: $WEBSITE_URL
API URL: $API_URL
Region: $REGION
"@

$deploymentInfo | Out-File -FilePath "$FRONTEND_DIR/deployment-info.txt" -Encoding UTF8
Write-Host "✓ Deployment info saved to deployment-info.txt`n" -ForegroundColor Green
