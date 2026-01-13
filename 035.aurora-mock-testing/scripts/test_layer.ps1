param(
    [string]$FunctionName = "test-layer-import",
    [string]$Region = "ap-northeast-1",
    [switch]$IncludeDependencies
)

$ErrorActionPreference = "Stop"

Write-Host "Building Lambda layer..." -ForegroundColor Green
if ($IncludeDependencies) {
    .\scripts\build_layer.ps1 -IncludeDependencies
} else {
    .\scripts\build_layer.ps1
}

Write-Host "`nCreating Lambda function package..." -ForegroundColor Green
if (Test-Path "lambda-package.zip") {
    Remove-Item "lambda-package.zip" -Force
}
Compress-Archive -Path "scripts\lambda_function.py" -DestinationPath "lambda-package.zip" -Force

Write-Host "`nCreating IAM role..." -ForegroundColor Green
$RoleName = "$FunctionName-role"
$TrustPolicyFile = "trust-policy.json"
$TrustPolicyContent = @'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
'@
[System.IO.File]::WriteAllText((Join-Path $PWD $TrustPolicyFile), $TrustPolicyContent)

try {
    $Role = aws iam get-role --role-name $RoleName 2>$null | ConvertFrom-Json
    Write-Host "Role already exists: $RoleName"
    $RoleArn = $Role.Role.Arn
} catch {
    $Role = aws iam create-role --role-name $RoleName --assume-role-policy-document file://$TrustPolicyFile | ConvertFrom-Json
    $RoleArn = $Role.Role.Arn
    aws iam attach-role-policy --role-name $RoleName --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    Write-Host "Waiting for role to be ready..."
    Start-Sleep -Seconds 10
}

Remove-Item $TrustPolicyFile -Force

Write-Host "`nPublishing Lambda layer..." -ForegroundColor Green
$Layer = aws lambda publish-layer-version `
    --layer-name "$FunctionName-layer" `
    --zip-file fileb://dependencies-layer.zip `
    --compatible-runtimes python3.9 `
    --region $Region | ConvertFrom-Json

$LayerArn = $Layer.LayerVersionArn
Write-Host "Layer ARN: $LayerArn"

Write-Host "`nCreating Lambda function..." -ForegroundColor Green
try {
    aws lambda delete-function --function-name $FunctionName --region $Region 2>$null
    Start-Sleep -Seconds 2
} catch {}

aws lambda create-function `
    --function-name $FunctionName `
    --runtime python3.9 `
    --role $RoleArn `
    --handler lambda_function.lambda_handler `
    --zip-file fileb://lambda-package.zip `
    --layers $LayerArn `
    --region $Region

Write-Host "`nWaiting for function to be ready..." -ForegroundColor Green
Start-Sleep -Seconds 5

Write-Host "`nTesting Lambda function..." -ForegroundColor Green
$TestEvent = '{}'
aws lambda invoke `
    --function-name $FunctionName `
    --payload $TestEvent `
    --region $Region `
    response.json

Write-Host "`nLambda response:" -ForegroundColor Cyan
Get-Content response.json | ConvertFrom-Json | ConvertTo-Json -Depth 10

Write-Host "`nCleaning up..." -ForegroundColor Green
Remove-Item lambda-package.zip -Force
Remove-Item response.json -Force

Write-Host "`nDone! Function created: $FunctionName" -ForegroundColor Green
Write-Host "To delete: aws lambda delete-function --function-name $FunctionName --region $Region"
