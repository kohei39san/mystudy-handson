#!/usr/bin/env pwsh
# Lambda Layer 完全デプロイメントスクリプト
# pydantic + psycopg2-binary のLambdaレイヤー作成、デプロイ、テスト

param(
    [string]$Profile = "default",
    [string]$StackName = "lambda-layer-test",
    [string]$BucketName = "lambda-layers-default-20260107"
)

Write-Host "=== Lambda Layer Complete Deployment ===" -ForegroundColor Green
Write-Host "Profile: $Profile"
Write-Host "Stack: $StackName"
Write-Host "S3 Bucket: $BucketName"
Write-Host ""

# Step 1: Create Layer with Docker
Write-Host "Step 1: Creating Lambda Layer with Docker..." -ForegroundColor Yellow
try {
    .\create_layer_docker.ps1
    if ($LASTEXITCODE -ne 0) {
        throw "Layer creation failed"
    }
    Write-Host "✅ Layer created successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Layer creation failed: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Upload Layer to S3
Write-Host "Step 2: Uploading Layer to S3..." -ForegroundColor Yellow
$LayerFile = "pydantic-psycopg2-layer-linux.zip"
$LayerKey = "lambda-layers/$LayerFile"

try {
    aws s3 cp $LayerFile "s3://$BucketName/$LayerKey" --profile $Profile
    if ($LASTEXITCODE -ne 0) {
        throw "S3 upload failed"
    }
    Write-Host "✅ Layer uploaded to S3" -ForegroundColor Green
} catch {
    Write-Host "❌ S3 upload failed: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Deploy CloudFormation Stack
Write-Host "Step 3: Deploying CloudFormation Stack..." -ForegroundColor Yellow
try {
    # Check if stack exists
    $stackExists = aws cloudformation describe-stacks --stack-name $StackName --profile $Profile 2>$null
    
    if ($stackExists) {
        Write-Host "Stack exists, updating..." -ForegroundColor Cyan
        aws cloudformation update-stack --stack-name $StackName --template-body file://cloudformation-template.yaml --capabilities CAPABILITY_NAMED_IAM --profile $Profile
        if ($LASTEXITCODE -ne 0) {
            Write-Host "No changes detected or update failed" -ForegroundColor Yellow
        } else {
            Write-Host "Waiting for stack update..." -ForegroundColor Cyan
            aws cloudformation wait stack-update-complete --stack-name $StackName --profile $Profile
        }
    } else {
        Write-Host "Creating new stack..." -ForegroundColor Cyan
        aws cloudformation create-stack --stack-name $StackName --template-body file://cloudformation-template.yaml --capabilities CAPABILITY_NAMED_IAM --profile $Profile
        Write-Host "Waiting for stack creation..." -ForegroundColor Cyan
        aws cloudformation wait stack-create-complete --stack-name $StackName --profile $Profile
    }
    Write-Host "✅ CloudFormation deployment completed" -ForegroundColor Green
} catch {
    Write-Host "❌ CloudFormation deployment failed: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Create/Update Lambda Layer Version
Write-Host "Step 4: Publishing Lambda Layer Version..." -ForegroundColor Yellow
try {
    $LayerName = "$StackName-pydantic-psycopg2-layer"
    $LayerVersion = aws lambda publish-layer-version --layer-name $LayerName --description "Pydantic 2.12.4 and psycopg2-binary 2.9.11 for Python 3.13" --content S3Bucket=$BucketName,S3Key=$LayerKey --compatible-runtimes python3.13 --profile $Profile --query 'Version' --output text
    
    if ($LASTEXITCODE -ne 0) {
        throw "Layer version creation failed"
    }
    Write-Host "✅ Layer version $LayerVersion created" -ForegroundColor Green
} catch {
    Write-Host "❌ Layer version creation failed: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Update Lambda Function with New Layer
Write-Host "Step 5: Updating Lambda Function..." -ForegroundColor Yellow
try {
    $FunctionName = "$StackName-layer-test-function"
    $LayerArn = "arn:aws:lambda:ap-northeast-1:662615364564:layer:$LayerName:$LayerVersion"
    
    # Update Lambda function code if needed
    if (Test-Path "lambda_function.py") {
        Compress-Archive -Path "lambda_function.py" -DestinationPath "lambda-function.zip" -Force
        aws s3 cp "lambda-function.zip" "s3://$BucketName/lambda-function.zip" --profile $Profile
        aws lambda update-function-code --function-name $FunctionName --s3-bucket $BucketName --s3-key "lambda-function.zip" --profile $Profile
        Remove-Item "lambda-function.zip" -Force
    }
    
    # Update layer
    aws lambda update-function-configuration --function-name $FunctionName --layers $LayerArn --profile $Profile
    if ($LASTEXITCODE -ne 0) {
        throw "Function update failed"
    }
    Write-Host "✅ Lambda function updated with new layer" -ForegroundColor Green
} catch {
    Write-Host "❌ Lambda function update failed: $_" -ForegroundColor Red
    exit 1
}

# Step 6: Test Lambda Function
Write-Host "Step 6: Testing Lambda Function..." -ForegroundColor Yellow
try {
    $TestResult = aws lambda invoke --function-name $FunctionName --profile $Profile response.json --query 'StatusCode' --output text
    
    if ($TestResult -eq "200") {
        $Response = Get-Content response.json | ConvertFrom-Json
        $Body = $Response.body | ConvertFrom-Json
        
        Write-Host ""
        Write-Host "=== Test Results ===" -ForegroundColor Green
        Write-Host "Overall Status: $($Body.overall_status)" -ForegroundColor $(if ($Body.overall_status -eq "PASS") { "Green" } else { "Red" })
        Write-Host "Python Version: $($Body.python_version)"
        Write-Host ""
        Write-Host "Library Versions:" -ForegroundColor Cyan
        Write-Host "  pydantic: $($Body.tests.pydantic.version)"
        Write-Host "  psycopg2: $($Body.tests.psycopg2.version)"
        Write-Host ""
        Write-Host "Test Results:" -ForegroundColor Cyan
        $Body.tests.PSObject.Properties | ForEach-Object {
            $status = $_.Value.status
            $color = if ($status -eq "PASS") { "Green" } else { "Red" }
            Write-Host "  $($_.Name): $status" -ForegroundColor $color
        }
        
        if ($Body.overall_status -eq "PASS") {
            Write-Host ""
            Write-Host "🎉 All tests passed! Lambda Layer deployment successful!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "❌ Some tests failed. Check the details above." -ForegroundColor Red
            exit 1
        }
    } else {
        throw "Lambda invocation failed with status code: $TestResult"
    }
} catch {
    Write-Host "❌ Lambda function test failed: $_" -ForegroundColor Red
    exit 1
} finally {
    # Cleanup
    if (Test-Path "response.json") {
        Remove-Item "response.json" -Force
    }
}

Write-Host ""
Write-Host "=== Deployment Summary ===" -ForegroundColor Green
Write-Host "✅ Layer created and uploaded"
Write-Host "✅ CloudFormation stack deployed"
Write-Host "✅ Lambda layer version: $LayerVersion"
Write-Host "✅ Lambda function updated"
Write-Host "✅ All tests passed"
Write-Host ""
Write-Host "Ready for production use!" -ForegroundColor Green