# PowerShell Integration Test: Deploy and Validate StackSet
# 
# Usage:
#   .\test\deploy-and-test.ps1

$ErrorActionPreference = "Stop"

# Load .env file if exists
$envFile = Join-Path (Split-Path -Parent $PSScriptRoot) ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#].+?)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
        }
    }
    $awsProfile = $env:AWS_PROFILE
    if ($awsProfile) {
        Write-Host "Using AWS Profile: $awsProfile" -ForegroundColor Green
    }
}

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  StackSet Integration Test" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

# Step 1: Install dependencies
Write-Host "[1/4] Installing dependencies..." -ForegroundColor Yellow
Set-Location $ProjectDir
npm install --silent

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies." -ForegroundColor Red
    exit 1
}

# Step 2: Confirm parameters
Write-Host "[2/5] Please confirm parameter.ts settings..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Check: notification mode, target accounts, target regions" -ForegroundColor Gray
Write-Host "  Permission Model: $($env:STACK_SET_PERMISSION_MODEL)" -ForegroundColor Gray
if ($env:STACK_SET_PERMISSION_MODEL -eq "SELF_MANAGED") {
    Write-Host "  Make sure StackSet IAM roles are already created:" -ForegroundColor Gray
    Write-Host "    - AWSCloudFormationStackSetAdministrationRole (in management account)" -ForegroundColor Gray
    Write-Host "    - AWSCloudFormationStackSetExecutionRole (in target accounts)" -ForegroundColor Gray
}
Write-Host ""
$confirm = Read-Host "Have you confirmed the settings? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Test cancelled." -ForegroundColor Red
    exit 1
}

# Step 3: Bootstrap management account
Write-Host "[3/5] Checking CDK bootstrap status..." -ForegroundColor Yellow
$managementAccount = $env:STACK_SET_ACCOUNT
$managementRegion = $env:STACK_SET_REGION

if ($managementAccount -and $managementRegion) {
    Write-Host "  Management Account: $managementAccount" -ForegroundColor Gray
    Write-Host "  Region: $managementRegion" -ForegroundColor Gray
    Write-Host ""
    
    npx cdk bootstrap aws://$managementAccount/$managementRegion
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARNING] Bootstrap may have failed, but continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "[SUCCESS] Bootstrap completed." -ForegroundColor Green
    }
}
Write-Host ""

# Step 4: Deploy
Write-Host "[4/5] Deploying StackSet Manager Stack..." -ForegroundColor Yellow
Write-Host ""
npx cdk deploy Dev-BLEAGovBaseCtStackSetManager --require-approval never

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Deployment failed." -ForegroundColor Red
    exit 1
}

Write-Host "[SUCCESS] Deployment completed." -ForegroundColor Green
Write-Host ""

# Wait for StackInstances creation
Write-Host "[WAIT] Waiting for StackInstances creation (approx. 3-5 minutes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 180

# Step 5: Validate
Write-Host "[5/5] Validating StackSet status..." -ForegroundColor Yellow
Write-Host ""
npm run test:integration

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "  [SUCCESS] Integration test passed!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "  [ERROR] Integration test failed." -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
    exit 1
}

# Optional: Cleanup
Write-Host ""
$cleanup = Read-Host "Do you want to delete deployed resources? (y/N)"
if ($cleanup -eq "y" -or $cleanup -eq "Y") {
    Write-Host "[CLEANUP] Deleting resources..." -ForegroundColor Yellow
    npx cdk destroy Dev-BLEAGovBaseCtStackSetManager --force
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Cleanup completed." -ForegroundColor Green
    }
}
