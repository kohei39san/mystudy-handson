# Script to update Lambda function code from separate Python files

param(
    [string]$StackName = "openapi-cognito-auth-dev",
    [string]$Region = "ap-northeast-1"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Updating Lambda Function Code ===" -ForegroundColor Green

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$LambdaDir = Join-Path $ScriptDir "lambda"

# Get Lambda function names from stack
$LoginLambdaName = aws cloudformation describe-stack-resources `
    --stack-name $StackName `
    --region $Region `
    --query "StackResources[?LogicalResourceId=='LoginLambda'].PhysicalResourceId" `
    --output text

$RefreshLambdaName = aws cloudformation describe-stack-resources `
    --stack-name $StackName `
    --region $Region `
    --query "StackResources[?LogicalResourceId=='RefreshTokenLambda'].PhysicalResourceId" `
    --output text

# Create temporary directory for Lambda packages
$TempDir = Join-Path $env:TEMP "lambda-packages"
if (Test-Path $TempDir) {
    Remove-Item $TempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $TempDir | Out-Null

# Update Login Lambda
Write-Host "Updating Login Lambda..." -ForegroundColor Yellow
$LoginZip = Join-Path $TempDir "login.zip"
Compress-Archive -Path (Join-Path $LambdaDir "login.py") -DestinationPath $LoginZip -Force
Rename-Item -Path (Join-Path $TempDir "login.py") -NewName "index.py" -ErrorAction SilentlyContinue

# Recreate zip with correct structure
$LoginTempDir = Join-Path $TempDir "login"
New-Item -ItemType Directory -Path $LoginTempDir | Out-Null
Copy-Item (Join-Path $LambdaDir "login.py") -Destination (Join-Path $LoginTempDir "index.py")
Compress-Archive -Path (Join-Path $LoginTempDir "index.py") -DestinationPath $LoginZip -Force

aws lambda update-function-code `
    --function-name $LoginLambdaName `
    --zip-file "fileb://$LoginZip" `
    --region $Region | Out-Null

Write-Host "[OK] Login Lambda updated" -ForegroundColor Green

# Update Refresh Lambda
Write-Host "Updating Refresh Token Lambda..." -ForegroundColor Yellow
$RefreshZip = Join-Path $TempDir "refresh.zip"
$RefreshTempDir = Join-Path $TempDir "refresh"
New-Item -ItemType Directory -Path $RefreshTempDir | Out-Null
Copy-Item (Join-Path $LambdaDir "refresh.py") -Destination (Join-Path $RefreshTempDir "index.py")
Compress-Archive -Path (Join-Path $RefreshTempDir "index.py") -DestinationPath $RefreshZip -Force

aws lambda update-function-code `
    --function-name $RefreshLambdaName `
    --zip-file "fileb://$RefreshZip" `
    --region $Region | Out-Null

Write-Host "[OK] Refresh Token Lambda updated" -ForegroundColor Green

# Cleanup
Remove-Item $TempDir -Recurse -Force

Write-Host "`n✓ All Lambda functions updated successfully!" -ForegroundColor Green
