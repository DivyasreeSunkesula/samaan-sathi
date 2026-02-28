# API Diagnostics Script for Windows PowerShell
# This script helps diagnose API Gateway deployment issues

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Samaan Sathi API Diagnostics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Get API Gateway ID
Write-Host "Step 1: Finding API Gateway..." -ForegroundColor Yellow
$apiId = aws cloudformation describe-stacks `
    --stack-name SamaanSathi-API-dev `
    --query 'Stacks[0].Outputs[?OutputKey==`ApiId`].OutputValue' `
    --output text

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($apiId)) {
    Write-Host "ERROR: Could not find API Gateway ID" -ForegroundColor Red
    Write-Host "Make sure the API stack is deployed successfully" -ForegroundColor Red
    exit 1
}

Write-Host "✓ API Gateway ID: $apiId" -ForegroundColor Green
Write-Host ""

# Step 2: Get API URL
Write-Host "Step 2: Getting API URL..." -ForegroundColor Yellow
$apiUrl = aws cloudformation describe-stacks `
    --stack-name SamaanSathi-API-dev `
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' `
    --output text

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($apiUrl)) {
    Write-Host "ERROR: Could not find API URL" -ForegroundColor Red
    exit 1
}

Write-Host "✓ API URL: $apiUrl" -ForegroundColor Green
Write-Host ""

# Step 3: Check API Gateway deployment
Write-Host "Step 3: Checking API Gateway deployment..." -ForegroundColor Yellow
$deployments = aws apigateway get-deployments --rest-api-id $apiId --query 'items[0]' --output json | ConvertFrom-Json

if ($null -eq $deployments) {
    Write-Host "ERROR: No deployments found for API Gateway" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Latest deployment ID: $($deployments.id)" -ForegroundColor Green
Write-Host "✓ Created at: $($deployments.createdDate)" -ForegroundColor Green
Write-Host ""

# Step 4: List API resources
Write-Host "Step 4: Listing API resources..." -ForegroundColor Yellow
$resources = aws apigateway get-resources --rest-api-id $apiId --output json | ConvertFrom-Json

Write-Host "✓ Found $($resources.items.Count) resources:" -ForegroundColor Green
foreach ($resource in $resources.items) {
    $methods = if ($resource.resourceMethods) { 
        ($resource.resourceMethods.PSObject.Properties.Name -join ", ")
    } else { 
        "No methods" 
    }
    Write-Host "  - $($resource.path) [$methods]" -ForegroundColor Cyan
}
Write-Host ""

# Step 5: Check if /auth/register exists
Write-Host "Step 5: Verifying /auth/register endpoint..." -ForegroundColor Yellow
$authRegister = $resources.items | Where-Object { $_.path -eq "/auth/register" }

if ($null -eq $authRegister) {
    Write-Host "ERROR: /auth/register endpoint not found!" -ForegroundColor Red
    Write-Host "Available paths:" -ForegroundColor Yellow
    $resources.items | ForEach-Object { Write-Host "  - $($_.path)" -ForegroundColor Cyan }
    exit 1
}

Write-Host "✓ /auth/register endpoint exists" -ForegroundColor Green
Write-Host ""

# Step 6: Test API endpoint
Write-Host "Step 6: Testing API endpoint..." -ForegroundColor Yellow
Write-Host "Testing: POST $apiUrl/auth/register" -ForegroundColor Cyan

$testBody = @{
    username = "testuser$(Get-Random -Maximum 9999)"
    password = "TempPass$(Get-Random -Maximum 9999)!"
    email = "test$(Get-Random -Maximum 9999)@example.com"
    phone = "+919876543210"
    fullName = "Test User"
    shopName = "Test Shop"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest `
        -Uri "$apiUrl/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $testBody `
        -UseBasicParsing `
        -ErrorAction Stop

    Write-Host "✓ API is responding!" -ForegroundColor Green
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    Write-Host $response.Content -ForegroundColor White
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $errorBody = $_.ErrorDetails.Message
    
    if ($statusCode -eq 403) {
        Write-Host "⚠ Got 403 Forbidden - This might be a Cognito configuration issue" -ForegroundColor Yellow
        Write-Host "Response: $errorBody" -ForegroundColor Yellow
    } elseif ($statusCode -eq 500) {
        Write-Host "⚠ Got 500 Internal Server Error - Check Lambda logs" -ForegroundColor Yellow
        Write-Host "Response: $errorBody" -ForegroundColor Yellow
    } else {
        Write-Host "ERROR: API test failed" -ForegroundColor Red
        Write-Host "Status Code: $statusCode" -ForegroundColor Red
        Write-Host "Error: $errorBody" -ForegroundColor Red
    }
}

Write-Host ""

# Step 7: Check Lambda function
Write-Host "Step 7: Checking Auth Lambda function..." -ForegroundColor Yellow
$lambdaName = "samaan-sathi-auth-dev"
$lambdaInfo = aws lambda get-function --function-name $lambdaName --query 'Configuration' --output json 2>$null | ConvertFrom-Json

if ($null -eq $lambdaInfo) {
    Write-Host "ERROR: Lambda function '$lambdaName' not found" -ForegroundColor Red
} else {
    Write-Host "✓ Lambda function exists" -ForegroundColor Green
    Write-Host "  Runtime: $($lambdaInfo.Runtime)" -ForegroundColor Cyan
    Write-Host "  Last Modified: $($lambdaInfo.LastModified)" -ForegroundColor Cyan
    Write-Host "  Memory: $($lambdaInfo.MemorySize) MB" -ForegroundColor Cyan
    Write-Host "  Timeout: $($lambdaInfo.Timeout) seconds" -ForegroundColor Cyan
}

Write-Host ""

# Step 8: Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your API URL (use this in test-ui.html):" -ForegroundColor Yellow
Write-Host $apiUrl -ForegroundColor Green
Write-Host ""
Write-Host "To test manually with curl:" -ForegroundColor Yellow
Write-Host "curl -X POST `"$apiUrl/auth/register`" -H `"Content-Type: application/json`" -d '{`"username`":`"[username]`",`"password`":`"[password]`",`"email`":`"[email]`",`"phone`":`"+91XXXXXXXXXX`",`"fullName`":`"[name]`"}'" -ForegroundColor Cyan
Write-Host ""

# Step 9: Check recent Lambda logs
Write-Host "Step 9: Checking recent Lambda logs..." -ForegroundColor Yellow
$logGroup = "/aws/lambda/$lambdaName"
$recentLogs = aws logs tail $logGroup --since 10m --format short 2>$null

if ($LASTEXITCODE -eq 0 -and ![string]::IsNullOrWhiteSpace($recentLogs)) {
    Write-Host "✓ Recent Lambda logs:" -ForegroundColor Green
    Write-Host $recentLogs -ForegroundColor White
} else {
    Write-Host "⚠ No recent logs found (this is normal if Lambda hasn't been invoked yet)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Diagnostics Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
