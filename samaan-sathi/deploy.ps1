# Samaan Sathi AI - Simple Deployment Script
# Handles all deployment scenarios

param(
    [string]$Action = "menu"
)

$ErrorActionPreference = "Stop"

function Show-Menu {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  Samaan Sathi AI - Deployment Menu" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Write-Host "1. Deploy Backend (First time)" -ForegroundColor White
    Write-Host "2. Fix Login Issue (Redeploy Auth)" -ForegroundColor White
    Write-Host "3. Confirm User Manually" -ForegroundColor White
    Write-Host "4. Test Frontend Locally" -ForegroundColor White
    Write-Host "5. Deploy Frontend to S3" -ForegroundColor White
    Write-Host "6. Get API URL" -ForegroundColor White
    Write-Host "7. Exit`n" -ForegroundColor White
    
    $choice = Read-Host "Select option (1-7)"
    return $choice
}

function Deploy-Backend {
    Write-Host "`nDeploying Backend..." -ForegroundColor Yellow
    Push-Location infrastructure
    npm install
    cdk deploy --all --require-approval never
    Pop-Location
    Write-Host "SUCCESS: Backend deployed`n" -ForegroundColor Green
}

function Fix-Auth {
    Write-Host "`nFixing Auth Configuration..." -ForegroundColor Yellow
    Push-Location infrastructure
    cdk deploy SamaanSathi-Auth-dev SamaanSathi-Compute-dev --require-approval never
    Pop-Location
    Write-Host "SUCCESS: Auth fixed. New users will auto-confirm`n" -ForegroundColor Green
}

function Confirm-User {
    Write-Host "`nConfirm User" -ForegroundColor Yellow
    
    try {
        $POOL_ID = aws cloudformation describe-stacks `
            --stack-name SamaanSathi-Auth-dev `
            --query 'Stacks[0].Outputs[?OutputKey==``UserPoolId``].OutputValue' `
            --output text 2>&1
        
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($POOL_ID)) {
            Write-Host "ERROR: User Pool not found. Deploy backend first (option 1)`n" -ForegroundColor Red
            return
        }
    } catch {
        Write-Host "ERROR: Cannot connect to AWS`n" -ForegroundColor Red
        return
    }
    
    Write-Host "User Pool ID: $POOL_ID" -ForegroundColor Green
    $username = Read-Host "`nEnter username to confirm"
    
    if ([string]::IsNullOrWhiteSpace($username)) {
        Write-Host "ERROR: Username required`n" -ForegroundColor Red
        return
    }
    
    try {
        aws cognito-idp admin-confirm-sign-up --user-pool-id $POOL_ID --username $username 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "SUCCESS: User '$username' confirmed!" -ForegroundColor Green
            Write-Host "You can now login with this account`n" -ForegroundColor Green
        } else {
            Write-Host "ERROR: Failed to confirm user. User may not exist or already confirmed`n" -ForegroundColor Red
        }
    } catch {
        Write-Host "ERROR: Failed to confirm user`n" -ForegroundColor Red
    }
}

function Test-Local {
    Write-Host "`nStarting Local Server..." -ForegroundColor Yellow
    
    try {
        $API_URL = aws cloudformation describe-stacks `
            --stack-name SamaanSathi-API-dev `
            --query 'Stacks[0].Outputs[?OutputKey==``ApiUrl``].OutputValue' `
            --output text 2>&1
        
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($API_URL)) {
            Write-Host "ERROR: Backend not deployed. Deploy backend first (option 1)`n" -ForegroundColor Red
            return
        }
    } catch {
        Write-Host "ERROR: Cannot connect to AWS. Check AWS CLI configuration`n" -ForegroundColor Red
        return
    }
    
    Write-Host "API URL: $API_URL" -ForegroundColor Green
    
    # Update config
    $config = @"
const CONFIG = {
    API_URL: '$API_URL',
    FEATURES: { ENABLE_AUTO_REFRESH: true, REFRESH_INTERVAL: 30000 },
    ENDPOINTS: {
        AUTH_REGISTER: '/auth/register', AUTH_LOGIN: '/auth/login',
        INVENTORY: '/inventory', UDHAAR: '/udhaar', UDHAAR_PAYMENT: '/udhaar/payment',
        FORECAST: '/forecast', FORECAST_DEMAND: '/forecast/demand',
        PRICING: '/pricing/recommendations', RECOMMENDATIONS: '/recommendations',
        ALERTS: '/alerts', OCR_PROCESS: '/ocr/process'
    },
    UI: { ITEMS_PER_PAGE: 20, TOAST_DURATION: 5000 }
};
"@
    
    try {
        $config | Out-File -FilePath "frontend/config.js" -Encoding UTF8 -Force
        Write-Host "Config updated successfully" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Cannot write config file`n" -ForegroundColor Red
        return
    }
    
    Write-Host "`nFrontend: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API: $API_URL" -ForegroundColor Cyan
    Write-Host "`nOpening browser...`n" -ForegroundColor Yellow
    
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8000"
    
    Write-Host "Starting Python HTTP server..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow
    
    Push-Location frontend
    try {
        python -m http.server 8000
    } catch {
        Write-Host "`nERROR: Python not found. Install Python or use Node.js:`n" -ForegroundColor Red
        Write-Host "  npx http-server -p 8000`n" -ForegroundColor Yellow
    }
    Pop-Location
}

function Deploy-Frontend {
    Write-Host "`nDeploying Frontend to S3..." -ForegroundColor Yellow
    
    $API_URL = aws cloudformation describe-stacks `
        --stack-name SamaanSathi-API-dev `
        --query 'Stacks[0].Outputs[?OutputKey==``ApiUrl``].OutputValue' `
        --output text 2>$null
    
    if (-not $API_URL) {
        Write-Host "ERROR: Backend not deployed`n" -ForegroundColor Red
        return
    }
    
    $BUCKET = "samaan-sathi-$(Get-Date -Format 'yyyyMMddHHmmss')"
    
    # Update config
    $config = @"
const CONFIG = {
    API_URL: '$API_URL',
    FEATURES: { ENABLE_AUTO_REFRESH: true, REFRESH_INTERVAL: 30000 },
    ENDPOINTS: {
        AUTH_REGISTER: '/auth/register', AUTH_LOGIN: '/auth/login',
        INVENTORY: '/inventory', UDHAAR: '/udhaar', UDHAAR_PAYMENT: '/udhaar/payment',
        FORECAST: '/forecast', FORECAST_DEMAND: '/forecast/demand',
        PRICING: '/pricing/recommendations', RECOMMENDATIONS: '/recommendations',
        ALERTS: '/alerts', OCR_PROCESS: '/ocr/process'
    },
    UI: { ITEMS_PER_PAGE: 20, TOAST_DURATION: 5000 }
};
"@
    $config | Out-File -FilePath "frontend/config.js" -Encoding UTF8
    
    aws s3 mb s3://$BUCKET --region ap-south-1
    aws s3 website s3://$BUCKET --index-document index.html
    
    $policy = @"
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::$BUCKET/*"}]}
"@
    $policy | Out-File -FilePath "$env:TEMP/policy.json" -Encoding UTF8
    aws s3api put-bucket-policy --bucket $BUCKET --policy file:///$env:TEMP/policy.json
    
    aws s3 sync frontend s3://$BUCKET --exclude "*.md" --delete
    
    $URL = "http://$BUCKET.s3-website.ap-south-1.amazonaws.com"
    Write-Host "`nSUCCESS: Frontend deployed!" -ForegroundColor Green
    Write-Host "URL: $URL`n" -ForegroundColor Cyan
}

function Get-ApiUrl {
    Write-Host "`nGetting API URL..." -ForegroundColor Yellow
    
    try {
        $API_URL = aws cloudformation describe-stacks `
            --stack-name SamaanSathi-API-dev `
            --query 'Stacks[0].Outputs[?OutputKey==``ApiUrl``].OutputValue' `
            --output text 2>&1
        
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($API_URL)) {
            Write-Host "`nAPI URL: $API_URL`n" -ForegroundColor Cyan
        } else {
            Write-Host "`nERROR: Backend not deployed. Deploy backend first (option 1)`n" -ForegroundColor Red
        }
    } catch {
        Write-Host "`nERROR: Cannot connect to AWS`n" -ForegroundColor Red
    }
}

# Main execution
if ($Action -eq "menu") {
    while ($true) {
        $choice = Show-Menu
        
        switch ($choice) {
            "1" { Deploy-Backend }
            "2" { Fix-Auth }
            "3" { Confirm-User }
            "4" { Test-Local }
            "5" { Deploy-Frontend }
            "6" { Get-ApiUrl }
            "7" { exit 0 }
            default { Write-Host "Invalid option`n" -ForegroundColor Red }
        }
    }
} else {
    switch ($Action) {
        "backend" { Deploy-Backend }
        "fix" { Fix-Auth }
        "confirm" { Confirm-User }
        "local" { Test-Local }
        "frontend" { Deploy-Frontend }
        "url" { Get-ApiUrl }
    }
}
