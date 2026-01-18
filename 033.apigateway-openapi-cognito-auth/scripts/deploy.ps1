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
$CedarSchemaPath = Join-Path $ProjectDir "src\schema.json"
$AvpPoliciesDir = Join-Path $ProjectDir "src\avp-policies"
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

# Build parameter overrides (optionally include Verified Permissions schema)
$paramOverrides = @(
    "Environment=$Environment",
    "ProjectName=$ProjectName"
)

$avpSchemaJson = $null
$avpPolicies = @()

if (Test-Path $CedarSchemaPath) {
    Write-Host "Found AVP schema at $CedarSchemaPath; enabling Verified Permissions" -ForegroundColor Yellow
    # Read and compact JSON for later use
    $schemaContent = Get-Content $CedarSchemaPath -Raw
    $avpSchemaJson = ($schemaContent | ConvertFrom-Json | ConvertTo-Json -Compress -Depth 10)
    
    $paramOverrides += "EnableVerifiedPermissions=true"
    $paramOverrides += "PrincipalEntityType=User"
    
    # Collect all Cedar policy files from avp-policies directory
    if (Test-Path $AvpPoliciesDir) {
        $cedarFiles = Get-ChildItem -Path $AvpPoliciesDir -Filter "*.cedar" -ErrorAction SilentlyContinue
        foreach ($cedarFile in $cedarFiles) {
            $avpPolicies += @{
                Path = $cedarFile.FullName
                Description = "Policy from $($cedarFile.Name)"
            }
        }
    }
} else {
    $paramOverrides += "EnableVerifiedPermissions=false"
}

# Deploy CloudFormation stack
aws cloudformation deploy `
    --template-file $CfnTemplate `
    --stack-name $StackName `
    --parameter-overrides $paramOverrides `
    --capabilities CAPABILITY_NAMED_IAM `
    --region $Region `
    --no-fail-on-empty-changeset

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ CloudFormation stack deployed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ CloudFormation deployment failed" -ForegroundColor Red
    exit 1
}

# Update AVP schema and policies if schema file exists
# (This runs regardless of whether CloudFormation had changes, so existing stacks get updated)
if ($avpSchemaJson) {
    Write-Host "[Post-Deploy] Updating AVP PolicyStore schema and policies..." -ForegroundColor Cyan
    $policyStoreId = aws cloudformation describe-stacks `
        --stack-name $StackName `
        --region $Region `
        --query "Stacks[0].Outputs[?OutputKey=='AvpPolicyStoreId'].OutputValue" `
        --output text
    
    if ($policyStoreId -and $policyStoreId -ne "None") {
        # Write schema definition to temp file for put-schema
        $schemaDefFile = Join-Path $env:TEMP "avp-schema-def-$(Get-Date -Format 'yyyyMMddHHmmssffff').json"
        # Compact the schema JSON and wrap it as cedarJson string value
        $schemaCompact = $schemaContent | ConvertFrom-Json | ConvertTo-Json -Compress -Depth 10
        # Escape the compacted schema for JSON string
        $schemaEscaped = $schemaCompact -replace '\\', '\\' -replace '"', '\"'
        $schemaInput = "{`"cedarJson`": `"$schemaEscaped`"}"
        [System.IO.File]::WriteAllText($schemaDefFile, $schemaInput, [System.Text.UTF8Encoding]::new($false))
        
        aws verifiedpermissions put-schema `
            --policy-store-id $policyStoreId `
            --region $Region `
            --definition "file://$schemaDefFile"
        
        $schemaResult = $LASTEXITCODE
        Remove-Item $schemaDefFile -ErrorAction SilentlyContinue
        
        if ($schemaResult -eq 0) {
            Write-Host "✓ AVP schema updated successfully" -ForegroundColor Green
        } else {
            Write-Host "⚠ Failed to update AVP schema (may already exist)" -ForegroundColor Yellow
        }
        
        # Delete all existing policies before creating new ones
        Write-Host "[Post-Deploy] Deleting existing AVP policies..." -ForegroundColor Cyan
        $existingPolicies = aws verifiedpermissions list-policies `
            --policy-store-id $policyStoreId `
            --region $Region `
            --query 'policies[].policyId' `
            --output text 2>$null
        
        if ($existingPolicies) {
            $policyIds = $existingPolicies -split '\s+'
            foreach ($policyId in $policyIds) {
                if ($policyId.Trim()) {
                    Write-Host "  Deleting policy: $policyId" -ForegroundColor Gray
                    aws verifiedpermissions delete-policy `
                        --policy-store-id $policyStoreId `
                        --policy-id $policyId `
                        --region $Region 2>&1 | Out-Null
                    
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "  ✓ Policy deleted: $policyId" -ForegroundColor Green
                    } else {
                        Write-Host "  ⚠ Failed to delete policy: $policyId" -ForegroundColor Yellow
                    }
                }
            }
        } else {
            Write-Host "  No existing policies to delete" -ForegroundColor Gray
        }
        
        # Create policies regardless of schema update result (policies may not exist yet)
        Write-Host "Debug: avpPolicies count = $($avpPolicies.Count)" -ForegroundColor Gray
        foreach ($p in $avpPolicies) {
            Write-Host "Debug: Policy file = $($p.Path)" -ForegroundColor Gray
            Write-Host "Debug: Policy exists = $(Test-Path $p.Path)" -ForegroundColor Gray
        }
        
        if ($avpPolicies.Count -gt 0) {
            Write-Host "[Post-Deploy] Creating AVP policies..." -ForegroundColor Cyan
            foreach ($policy in $avpPolicies) {
                $policyStatement = Get-Content $policy.Path -Raw
                # Remove any markdown code block markers that might exist in the file
                $policyStatement = $policyStatement -replace '(?s)^```.*?[\r\n]+', '' -replace '(?s)[\r\n]+```\s*$', ''
                # Trim leading/trailing whitespace
                $policyStatement = $policyStatement.Trim()
                
                $policyName = Split-Path $policy.Path -Leaf
                
                Write-Host "  Creating policy from $policyName..." -ForegroundColor Gray
                
                # Create policy definition JSON
                $policyDef = @{
                    static = @{
                        description = $policy.Description
                        statement = $policyStatement
                    }
                } | ConvertTo-Json -Compress -Depth 10
                
                $policyDefFile = Join-Path $env:TEMP "avp-policy-$(Get-Date -Format 'yyyyMMddHHmmssffff').json"
                [System.IO.File]::WriteAllText($policyDefFile, $policyDef, [System.Text.UTF8Encoding]::new($false))
                
                aws verifiedpermissions create-policy `
                    --policy-store-id $policyStoreId `
                    --region $Region `
                    --definition "file://$policyDefFile"
                
                Remove-Item $policyDefFile -ErrorAction SilentlyContinue
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  ✓ Policy created from $policyName" -ForegroundColor Green
                } else {
                    Write-Host "  ✗ Failed to create policy from $policyName" -ForegroundColor Red
                }
            }
        } else {
            Write-Host "⚠ No policies to create (avpPolicies is empty)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠ Could not retrieve PolicyStore ID - skipping AVP schema/policy updates" -ForegroundColor Yellow
    }
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

$AvpPolicyStoreId = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`AvpPolicyStoreId`].OutputValue' `
    --output text 2>$null

$RevokeTokenLambdaArn = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`RevokeTokenLambdaArn`].OutputValue' `
    --output text 2>$null

$ApiGatewayRoleArn = aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayRoleArn`].OutputValue' `
    --output text 2>$null

# Import users from CSV
Write-Host "`nImporting users from CSV..." -ForegroundColor Yellow

$users = Import-Csv -Path $UsersCSV
$userCredentials = @()

foreach ($user in $users) {
    # Check if user exists
    $existingUser = $null
    try {
        $existingUser = aws cognito-idp admin-get-user `
            --user-pool-id $UserPoolId `
            --username $user.username `
            --region $Region 2>&1
    } catch {
        # User does not exist, continue with creation
    }
    
    if ($existingUser -and $existingUser -notmatch "UserNotFoundException") {
        Write-Host "User $($user.username) already exists, updating password and group..." -ForegroundColor Yellow
        
        # Fixed password for testing (consider using a parameter or secure method in production)
        $password = "TempPass123!@#"
        
        # Update password for existing user
        $setPasswordResult = aws cognito-idp admin-set-user-password `
            --user-pool-id $UserPoolId `
            --username $user.username `
            --password $password `
            --permanent `
            --region $Region 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Failed to update password for user $($user.username)" -ForegroundColor Red
            continue
        }
        
        # Ensure user is in the correct group
        $addGroupResult = aws cognito-idp admin-add-user-to-group `
            --user-pool-id $UserPoolId `
            --username $user.username `
            --group-name $user.group `
            --region $Region 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Password updated and user added to $($user.group) for $($user.username)" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] Password updated but failed to add user $($user.username) to group $($user.group)" -ForegroundColor Yellow
        }
        continue
    }
    
    Write-Host "Creating user: $($user.username)..."
    
    # Fixed password for testing (consider using a parameter or secure method in production)
    $password = "TempPass123!@#"
    
    # Create user
    $createResult = aws cognito-idp admin-create-user `
        --user-pool-id $UserPoolId `
        --username $user.username `
        --message-action SUPPRESS `
        --region $Region 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create user $($user.username)" -ForegroundColor Red
        continue
    }
    
    # Set password
    $setPasswordResult = aws cognito-idp admin-set-user-password `
        --user-pool-id $UserPoolId `
        --username $user.username `
        --password $password `
        --permanent `
        --region $Region 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to set password for user $($user.username)" -ForegroundColor Red
        continue
    }
    
    # Add to group
    $addGroupResult = aws cognito-idp admin-add-user-to-group `
        --user-pool-id $UserPoolId `
        --username $user.username `
        --group-name $user.group `
        --region $Region 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to add user $($user.username) to group $($user.group)" -ForegroundColor Red
        continue
    }
    
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

# Validate required variables
Write-Host "Debug: Checking variables..." -ForegroundColor Cyan
Write-Host "  AuthorizerLambdaArn: $AuthorizerLambdaArn" -ForegroundColor Gray
Write-Host "  ApiGatewayRoleArn: $ApiGatewayRoleArn" -ForegroundColor Gray
Write-Host "  UserPoolArn: $UserPoolArn" -ForegroundColor Gray

if ([string]::IsNullOrWhiteSpace($AuthorizerLambdaArn)) {
    Write-Host "[WARNING] AuthorizerLambdaArn is empty" -ForegroundColor Yellow
}
if ([string]::IsNullOrWhiteSpace($ApiGatewayRoleArn)) {
    Write-Host "[WARNING] ApiGatewayRoleArn is empty" -ForegroundColor Yellow
}

$OpenApiSpecProcessed = Join-Path $env:TEMP "openapi-spec-processed.yaml"
$OpenApiContent = Get-Content $OpenApiSpec -Raw

# Replace placeholders in OpenAPI spec
Write-Host "Replacing placeholders..." -ForegroundColor Yellow
$OpenApiContent = $OpenApiContent -replace '\{\{CognitoUserPoolArn\}\}', $UserPoolArn
$OpenApiContent = $OpenApiContent -replace '\{\{LambdaAuthorizerUri\}\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${AuthorizerLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\{\{BackendLambdaUri\}\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${BackendLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\{\{LoginLambdaUri\}\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${LoginLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\{\{RefreshTokenLambdaUri\}\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${RefreshTokenLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\{\{RevokeTokenLambdaUri\}\}', "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${RevokeTokenLambdaArn}/invocations"
$OpenApiContent = $OpenApiContent -replace '\{\{ApiGatewayRole\}\}', $ApiGatewayRoleArn

# Count remaining placeholders
$remainingCount = ($OpenApiContent | Select-String -Pattern '\{\{' -AllMatches | Measure-Object -Line).Lines
Write-Host "Remaining unresolved placeholders: $remainingCount" -ForegroundColor Yellow

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
aws apigateway put-rest-api --no-paginate `
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

# Update Authorizer Lambda
$AuthorizerLambdaName = $AuthorizerLambdaArn.Split(':')[-1]
$AuthorizerTempDir = Join-Path $TempDir "authorizer"
New-Item -ItemType Directory -Path $AuthorizerTempDir | Out-Null
Copy-Item (Join-Path $ProjectDir "scripts\lambda\authorizer.py") -Destination (Join-Path $AuthorizerTempDir "index.py")

# Install dependencies for Authorizer directly to the temp directory
if (Test-Path (Join-Path $ProjectDir "scripts\lambda\requirements.txt")) {
    pip install -r (Join-Path $ProjectDir "scripts\lambda\requirements.txt") -t $AuthorizerTempDir | Out-Null
}

$AuthorizerZip = Join-Path $TempDir "authorizer.zip"
Compress-Archive -Path (Join-Path $AuthorizerTempDir "*") -DestinationPath $AuthorizerZip -Force

aws lambda update-function-code `
    --function-name $AuthorizerLambdaName `
    --zip-file "fileb://$AuthorizerZip" `
    --region $Region | Out-Null

Write-Host "[OK] Authorizer Lambda code updated" -ForegroundColor Green

# Update Backend Lambda
$BackendLambdaName = $BackendLambdaArn.Split(':')[-1]
$BackendTempDir = Join-Path $TempDir "backend"
New-Item -ItemType Directory -Path $BackendTempDir | Out-Null
Copy-Item (Join-Path $ProjectDir "scripts\lambda\backend.py") -Destination (Join-Path $BackendTempDir "index.py")
$BackendZip = Join-Path $TempDir "backend.zip"
Compress-Archive -Path (Join-Path $BackendTempDir "index.py") -DestinationPath $BackendZip -Force

aws lambda update-function-code `
    --function-name $BackendLambdaName `
    --zip-file "fileb://$BackendZip" `
    --region $Region | Out-Null

Write-Host "[OK] Backend Lambda code updated" -ForegroundColor Green

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
if ($AvpPolicyStoreId -and $AvpPolicyStoreId -ne "None") {
    Write-Host "AVP Policy Store ID: $AvpPolicyStoreId" -ForegroundColor Yellow
}

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
