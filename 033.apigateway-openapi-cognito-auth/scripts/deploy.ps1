# API Gateway + OpenAPI + Cognito + Lambda Authorizer Deployment Script

param(
    [string]$StackName = "openapi-cognito-auth-dev",
    [string]$Region = "ap-northeast-1",
    [string]$ProjectName = "openapi-cognito-auth",
    [string]$Environment = "dev",
    [string]$UserEmail = "test@example.com",
    [string]$AdminEmail = "admin@example.com"
)

$ErrorActionPreference = "Stop"

Write-Host "=== API Gateway OpenAPI Cognito Auth Deployment ===" -ForegroundColor Green

# Check if AWS CLI is configured
try {
    $accountId = aws sts get-caller-identity --query 'Account' --output text 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "AWS CLI is not configured or credentials are invalid"
    }
    Write-Host "Current AWS Account: $accountId" -ForegroundColor Yellow
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

Write-Host "Project Directory: $ProjectDir" -ForegroundColor Yellow

# Validate required files exist
$CfnTemplate = Join-Path $ProjectDir "cfn\infrastructure.yaml"
$OpenApiSpec = Join-Path $ProjectDir "src\openapi-spec.yaml"
$OpenApiMerged = Join-Path $ProjectDir "src\openapi-merged.yaml"
$UsersCSV = Join-Path $ProjectDir "src\users.csv"

if (-not (Test-Path $CfnTemplate)) {
    Write-Host "Error: CloudFormation template not found at $CfnTemplate" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $OpenApiSpec)) {
    Write-Host "Error: OpenAPI specification not found at $OpenApiSpec" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $UsersCSV)) {
    Write-Host "Error: Users CSV not found at $UsersCSV" -ForegroundColor Red
    exit 1
}

Write-Host "✓ All required files found" -ForegroundColor Green

# Deploy CloudFormation stack
Write-Host "Deploying CloudFormation stack: $StackName" -ForegroundColor Yellow

aws cloudformation deploy `
    --template-file $CfnTemplate `
    --stack-name $StackName `
    --parameter-overrides `
        Environment=$Environment `
        ProjectName=$ProjectName `
        UserEmail=$UserEmail `
        AdminEmail=$AdminEmail `
    --capabilities CAPABILITY_NAMED_IAM `
    --region $Region `
    --no-fail-on-empty-changeset

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ CloudFormation stack deployed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ CloudFormation deployment failed" -ForegroundColor Red
    exit 1
}

# Get stack outputs
Write-Host "Retrieving stack outputs..." -ForegroundColor Yellow

$UserPoolId = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`CognitoUserPoolId`].OutputValue' `
    --output text 2>$null

$UserPoolClientId = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`CognitoUserPoolClientId`].OutputValue' `
    --output text 2>$null

$BackendLambdaArn = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`BackendLambdaArn`].OutputValue' `
    --output text 2>$null

$AuthorizerLambdaArn = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`LambdaAuthorizerArn`].OutputValue' `
    --output text 2>$null

$ApiGatewayId = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayRestApiId`].OutputValue' `
    --output text 2>$null

$ApiEndpoint = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayEndpoint`].OutputValue' `
    --output text 2>$null

$UserPoolArn = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`CognitoUserPoolArn`].OutputValue' `
    --output text 2>$null

$LoginLambdaArn = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`LoginLambdaArn`].OutputValue' `
    --output text 2>$null

$RefreshTokenLambdaArn = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`RefreshTokenLambdaArn`].OutputValue' `
    --output text 2>$null

$RevokeTokenLambdaArn = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`RevokeTokenLambdaArn`].OutputValue' `
    --output text 2>$null

# Import users from CSV
Write-Host "`nImporting users from CSV..." -ForegroundColor Yellow

$users = Import-Csv -Path $UsersCSV
$userCredentials = @()

foreach ($user in $users) {
    # Check if user exists
    $existingUser = aws cognito-idp admin-get-user `
        --user-pool-id $UserPoolId `
        --username $user.username `
        --region $Region 2>$null
    
    if ($existingUser) {
        Write-Host "User $($user.username) already exists, skipping..." -ForegroundColor Yellow
        continue
    }
    
    Write-Host "Creating user: $($user.username)..."
    
    # Generate random password
    $password = -join ((65..90) + (97..122) + (48..57) + (33,35,36,37,38,42,43,45,61,63,64) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    
    # Create user
    aws cognito-idp admin-create-user `
        --user-pool-id $UserPoolId `
        --username $user.username `
        --message-action SUPPRESS `
        --region $Region 2>$null
    
    # Set password
    aws cognito-idp admin-set-user-password `
        --user-pool-id $UserPoolId `
        --username $user.username `
        --password $password `
        --permanent `
        --region $Region 2>$null
    
    # Add to group
    aws cognito-idp admin-add-user-to-group `
        --user-pool-id $UserPoolId `
        --username $user.username `
        --group-name $user.group `
        --region $Region 2>$null
    
    Write-Host "[OK] User $($user.username) created and added to $($user.group)" -ForegroundColor Green
    
    # Store credentials
    $userCredentials += [PSCustomObject]@{
        Username = $user.username
        Password = $password
        Group = $user.group
    }
}

# Output credentials
Write-Host "`n=== Generated User Credentials ===" -ForegroundColor Cyan
$userCredentials | Format-Table -AutoSize
Write-Host "IMPORTANT: Save these credentials securely. They will not be shown again." -ForegroundColor Yellow

# Merge OpenAPI files if openapi directory exists
if (Test-Path (Join-Path $ProjectDir "openapi")) {
    Write-Host "`nMerging OpenAPI specification files..." -ForegroundColor Yellow
    
    # Check if Python is available
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        Push-Location $ProjectDir
        python scripts\merge-openapi.py --openapi-dir openapi --output src\openapi-merged.yaml
        Pop-Location
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] OpenAPI files merged successfully" -ForegroundColor Green
            $OpenApiSpec = $OpenApiMerged
        } else {
            Write-Host "[WARNING] Failed to merge OpenAPI files, using existing spec" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[WARNING] Python not found, using existing OpenAPI spec" -ForegroundColor Yellow
    }
}

# Import OpenAPI specification
Write-Host "`nImporting OpenAPI specification..." -ForegroundColor Yellow

$OpenApiSpecProcessed = Join-Path $env:TEMP "openapi-spec-processed.yaml"
$OpenApiContent = Get-Content $OpenApiSpec -Raw

# Replace placeholders in OpenAPI spec
$OpenApiContent = $OpenApiContent -replace '\{\{CognitoUserPoolArn\}\}', $UserPoolArn
$OpenApiContent = $OpenApiContent -replace '\{\{LambdaAuthorizerUri\}\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${AuthorizerLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\{\{BackendLambdaUri\}\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${BackendLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\{\{LoginLambdaUri\}\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${LoginLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\{\{RefreshTokenLambdaUri\}\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${RefreshTokenLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\{\{RevokeTokenLambdaUri\}\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${RevokeTokenLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\{\{ApiGatewayRole\}\}', $ApiGatewayRoleArn
# Legacy placeholder support
$OpenApiContent = $OpenApiContent -replace '\$\{CognitoUserPoolArn\}', $UserPoolArn
$OpenApiContent = $OpenApiContent -replace '\$\{LambdaAuthorizerUri\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${AuthorizerLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\$\{BackendLambdaUri\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${BackendLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\$\{LoginLambdaUri\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${LoginLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\$\{RefreshTokenLambdaUri\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${RefreshTokenLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\$\{RevokeTokenLambdaUri\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${RevokeTokenLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\$\{ApiGatewayRole\}', $ApiGatewayRoleArn

[System.IO.File]::WriteAllText($OpenApiSpecProcessed, $OpenApiContent, [System.Text.Encoding]::UTF8)

# Import OpenAPI spec to API Gateway
aws apigateway put-rest-api `
    --rest-api-id $ApiGatewayId `
    --mode overwrite `
    --body "fileb://$OpenApiSpecProcessed" `
    --region $Region

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] OpenAPI specification imported successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to import OpenAPI specification" -ForegroundColor Red
}

# Update Lambda function code from separate Python files
Write-Host "`nUpdating Lambda function code..." -ForegroundColor Yellow

$LoginLambdaArn = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`LoginLambdaArn`].OutputValue' `
    --output text 2>$null

$RefreshTokenLambdaArn = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`RefreshTokenLambdaArn`].OutputValue' `
    --output text 2>$null

$LoginLambdaName = $LoginLambdaArn.Split(':')[-1]
$RefreshLambdaName = $RefreshTokenLambdaArn.Split(':')[-1]

# Create temporary directory for Lambda packages
$TempDir = Join-Path $env:TEMP "lambda-packages-$(Get-Date -Format 'yyyyMMddHHmmss')"
New-Item -ItemType Directory -Path $TempDir | Out-Null

# Update Login Lambda
$LoginTempDir = Join-Path $TempDir "login"
New-Item -ItemType Directory -Path $LoginTempDir | Out-Null
Copy-Item (Join-Path $ProjectDir "scripts\lambda\login.py") -Destination (Join-Path $LoginTempDir "index.py")
$LoginZip = Join-Path $TempDir "login.zip"
Compress-Archive -Path (Join-Path $LoginTempDir "index.py") -DestinationPath $LoginZip -Force

aws lambda update-function-code `
    --function-name $LoginLambdaName `
    --zip-file "fileb://$LoginZip" `
    --region $Region | Out-Null

Write-Host "[OK] Login Lambda code updated" -ForegroundColor Green

# Update Refresh Lambda
$RefreshTempDir = Join-Path $TempDir "refresh"
New-Item -ItemType Directory -Path $RefreshTempDir | Out-Null
Copy-Item (Join-Path $ProjectDir "scripts\lambda\refresh.py") -Destination (Join-Path $RefreshTempDir "index.py")
$RefreshZip = Join-Path $TempDir "refresh.zip"
Compress-Archive -Path (Join-Path $RefreshTempDir "index.py") -DestinationPath $RefreshZip -Force

aws lambda update-function-code `
    --function-name $RefreshLambdaName `
    --zip-file "fileb://$RefreshZip" `
    --region $Region | Out-Null

Write-Host "[OK] Refresh Token Lambda code updated" -ForegroundColor Green

# Cleanup
Remove-Item $TempDir -Recurse -Force

# Create new deployment
Write-Host "Creating new API deployment..." -ForegroundColor Yellow
$DeploymentId = aws apigateway create-deployment `
    --rest-api-id $ApiGatewayId `
    --stage-name $Environment `
    --description "Deployment with OpenAPI specification" `
    --region $Region `
    --query 'id' `
    --output text

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] API deployed successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to deploy API" -ForegroundColor Red
}

Write-Host "`n=== Deployment Summary ===" -ForegroundColor Green
Write-Host "Stack Name: $StackName" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host "User Pool ID: $UserPoolId" -ForegroundColor Yellow
Write-Host "User Pool Client ID: $UserPoolClientId" -ForegroundColor Yellow
Write-Host "API Gateway ID: $ApiGatewayId" -ForegroundColor Yellow
Write-Host "API Endpoint: $ApiEndpoint" -ForegroundColor Yellow
Write-Host "Backend Lambda ARN: $BackendLambdaArn" -ForegroundColor Yellow
Write-Host "Authorizer Lambda ARN: $AuthorizerLambdaArn" -ForegroundColor Yellow

Write-Host "`n=== Next Steps ===" -ForegroundColor Green
Write-Host "1. Test the API:"
Write-Host "   python scripts\test-api-simple.py --api-endpoint $ApiEndpoint --user-pool-id $UserPoolId --client-id $UserPoolClientId"
Write-Host ""
Write-Host "2. Test Cognito authentication:"
Write-Host "   python scripts\test-cognito-auth.py"
Write-Host ""

Write-Host "3. Test revoke API (admin only):"
Write-Host "   python src\test-revoke-api.py --endpoint $ApiEndpoint --username <target_username>"
Write-Host ""
Write-Host "✓ Deployment completed successfully!" -ForegroundColor Green

# Return outputs for use in other scripts
return @{
    UserPoolId = $UserPoolId
    UserPoolClientId = $UserPoolClientId
    ApiGatewayId = $ApiGatewayId
    ApiEndpoint = $ApiEndpoint
    BackendLambdaArn = $BackendLambdaArn
    AuthorizerLambdaArn = $AuthorizerLambdaArn
}
