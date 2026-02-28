# Quick script to get your API URL
# Run this to get the correct URL for test-ui.html

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Getting your API URL..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$apiUrl = aws cloudformation describe-stacks `
    --stack-name SamaanSathi-API-dev `
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' `
    --output text

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($apiUrl)) {
    Write-Host "ERROR: Could not find API URL" -ForegroundColor Red
    Write-Host "Make sure the API stack is deployed:" -ForegroundColor Yellow
    Write-Host "  cd infrastructure" -ForegroundColor Cyan
    Write-Host "  npx cdk deploy SamaanSathi-API-dev" -ForegroundColor Cyan
    exit 1
}

# Remove trailing slash if present
$apiUrl = $apiUrl.TrimEnd('/')

Write-Host "✓ Your API URL is:" -ForegroundColor Green
Write-Host ""
Write-Host "  $apiUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "How to use this URL:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open test-ui.html in your browser" -ForegroundColor White
Write-Host "2. Paste this URL in the Configuration section:" -ForegroundColor White
Write-Host ""
Write-Host "   $apiUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Click 'Save API URL'" -ForegroundColor White
Write-Host "4. Try registering a user" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Quick Test:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Testing /auth/register endpoint..." -ForegroundColor Yellow

$testBody = @{
    username = "quicktest$(Get-Random -Maximum 9999)"
    password = "TempPass$(Get-Random -Maximum 9999)!"
    email = "test$(Get-Random -Maximum 9999)@example.com"
    phone = "+919876543210"
    fullName = "Quick Test"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest `
        -Uri "$apiUrl/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $testBody `
        -UseBasicParsing `
        -ErrorAction Stop

    Write-Host "✓ SUCCESS! API is working!" -ForegroundColor Green
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Cyan
    $responseObj = $response.Content | ConvertFrom-Json
    Write-Host ($responseObj | ConvertTo-Json -Depth 10) -ForegroundColor White
    Write-Host ""
    Write-Host "✓ Your API is ready to use!" -ForegroundColor Green
    
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    
    if ($statusCode -eq 403) {
        Write-Host "⚠ Got 403 - Cognito might need configuration" -ForegroundColor Yellow
        Write-Host "But the API endpoint exists and is responding!" -ForegroundColor Yellow
    } elseif ($statusCode -eq 500) {
        Write-Host "⚠ Got 500 - Lambda function error" -ForegroundColor Yellow
        Write-Host "Check Lambda logs:" -ForegroundColor Yellow
        Write-Host "  aws logs tail /aws/lambda/samaan-sathi-auth-dev --follow" -ForegroundColor Cyan
    } elseif ($null -eq $statusCode) {
        Write-Host "✗ ERROR: Could not connect to API" -ForegroundColor Red
        Write-Host "This usually means 'Missing Authentication Token'" -ForegroundColor Red
        Write-Host ""
        Write-Host "Possible issues:" -ForegroundColor Yellow
        Write-Host "  1. API Gateway not fully deployed" -ForegroundColor White
        Write-Host "  2. Wrong URL format" -ForegroundColor White
        Write-Host ""
        Write-Host "Run full diagnostics:" -ForegroundColor Yellow
        Write-Host "  .\scripts\diagnose-api.ps1" -ForegroundColor Cyan
    } else {
        Write-Host "✗ ERROR: Status $statusCode" -ForegroundColor Red
        if ($_.ErrorDetails.Message) {
            Write-Host $_.ErrorDetails.Message -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Need more help?" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Run full diagnostics:" -ForegroundColor White
Write-Host "  .\scripts\diagnose-api.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check troubleshooting guide:" -ForegroundColor White
Write-Host "  API_TROUBLESHOOTING.md" -ForegroundColor Cyan
Write-Host ""
