param(
    [string]$StackName = "nested-sfn-study-dev",
    [string]$Region = "ap-northeast-1",
    [string]$Profile = "",
    [switch]$UpdateParentStateMachine,
    [switch]$UpdateChildStateMachine,
    [switch]$UpdateParentLambda,
    [switch]$UpdateChildLambda,
    [switch]$UpdateFilterLambda
)

$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $PSScriptRoot
$SrcDir = Join-Path $ProjectDir "src"
$AslDir = Join-Path $ProjectDir "asl"
$TmpDir = Join-Path $ProjectDir ".tmp_update"

$AwsArgs = @()
if ($Profile -and $Profile.Trim().Length -gt 0) {
    $AwsArgs += @("--profile", $Profile)
}
$AwsArgs += @("--region", $Region)

if (-not ($UpdateParentStateMachine -or $UpdateChildStateMachine -or $UpdateParentLambda -or $UpdateChildLambda -or $UpdateFilterLambda)) {
    $UpdateParentStateMachine = $true
    $UpdateChildStateMachine = $true
    $UpdateParentLambda = $true
    $UpdateChildLambda = $true
    $UpdateFilterLambda = $true
}

Write-Host "===== Update Step Functions/Lambda from local src/asl ====="
Write-Host "Project Dir: $ProjectDir"
Write-Host "Stack Name : $StackName"
Write-Host "Region     : $Region"
Write-Host ""

$StackJson = aws cloudformation describe-stacks --stack-name $StackName --output json @AwsArgs
$Stack = ($StackJson | ConvertFrom-Json).Stacks[0]

function Get-ParamValue($key) {
    $match = $Stack.Parameters | Where-Object { $_.ParameterKey -eq $key }
    if (-not $match) {
        throw "Parameter key not found: $key"
    }
    return $match.ParameterValue
}

function Get-OutputValue($key) {
    $match = $Stack.Outputs | Where-Object { $_.OutputKey -eq $key }
    if (-not $match) {
        throw "Output key not found: $key"
    }
    return $match.OutputValue
}

$ProjectName = Get-ParamValue "ProjectName"
$Environment = Get-ParamValue "Environment"

$ParentLambdaName = Get-OutputValue "ParentLambdaFunctionName"
$ChildLambdaName = Get-OutputValue "ChildLambdaFunctionName"
$ParentLambdaArn = Get-OutputValue "ParentLambdaFunctionArn"
$ChildLambdaArn = Get-OutputValue "ChildLambdaFunctionArn"
$ParentStateMachineArn = Get-OutputValue "ParentStateMachineArn"
$ChildStateMachineArn = Get-OutputValue "ChildStateMachineArn"

$FilterLambdaName = "$ProjectName-$Environment-child-output-filter-lambda"
$FilterLambdaArn = (aws lambda get-function --function-name $FilterLambdaName --query "Configuration.FunctionArn" --output text @AwsArgs)

function Load-AslWithCfnRefs {
    param(
        [string]$Path,
        [string]$ParentLambdaArn,
        [string]$ChildStateMachineArn,
        [string]$FilterLambdaArn,
        [string]$ChildLambdaArn
    )

    $raw = Get-Content -Path $Path -Raw
    $raw = $raw.Replace('${parent_lambda_function_arn}', $ParentLambdaArn)
    $raw = $raw.Replace('${child_state_machine_arn}', $ChildStateMachineArn)
    $raw = $raw.Replace('${child_output_filter_lambda_arn}', $FilterLambdaArn)
    $raw = $raw.Replace('${child_lambda_function_arn}', $ChildLambdaArn)
    return $raw.Trim()
}

function Update-LambdaCode($FunctionName, $SourceFile) {
    $LambdaDir = Join-Path $TmpDir $FunctionName
    New-Item -ItemType Directory -Path $LambdaDir | Out-Null

    Copy-Item -Path $SourceFile -Destination (Join-Path $LambdaDir "index.py")

    $ZipPath = Join-Path $TmpDir "$FunctionName.zip"
    if (Test-Path $ZipPath) {
        Remove-Item $ZipPath
    }
    Compress-Archive -Path (Join-Path $LambdaDir "*") -DestinationPath $ZipPath

    Write-Host "Updating Lambda code: $FunctionName"
    aws lambda update-function-code --function-name $FunctionName --zip-file "fileb://$ZipPath" @AwsArgs | Out-Null
}

if (Test-Path $TmpDir) {
    Remove-Item -Recurse -Force $TmpDir
}
New-Item -ItemType Directory -Path $TmpDir | Out-Null

if ($UpdateParentStateMachine -or $UpdateChildStateMachine) {
    $ChildAsl = Load-AslWithCfnRefs -Path (Join-Path $AslDir "child_state_machine.json") -ParentLambdaArn $ParentLambdaArn -ChildStateMachineArn $ChildStateMachineArn -FilterLambdaArn $FilterLambdaArn -ChildLambdaArn $ChildLambdaArn
    $ParentAsl = Load-AslWithCfnRefs -Path (Join-Path $AslDir "parent_state_machine.json") -ParentLambdaArn $ParentLambdaArn -ChildStateMachineArn $ChildStateMachineArn -FilterLambdaArn $FilterLambdaArn -ChildLambdaArn $ChildLambdaArn

    $ChildAslFile = Join-Path $TmpDir "child_state_machine.json"
    $ParentAslFile = Join-Path $TmpDir "parent_state_machine.json"
    $ChildAsl | Set-Content -Path $ChildAslFile
    $ParentAsl | Set-Content -Path $ParentAslFile

    if ($UpdateChildStateMachine) {
        Write-Host "Updating child state machine..."
        aws stepfunctions update-state-machine --state-machine-arn $ChildStateMachineArn --definition "file://$ChildAslFile" @AwsArgs | Out-Null
    }

    if ($UpdateParentStateMachine) {
        Write-Host "Updating parent state machine..."
        aws stepfunctions update-state-machine --state-machine-arn $ParentStateMachineArn --definition "file://$ParentAslFile" @AwsArgs | Out-Null
    }
}

if ($UpdateParentLambda) {
    Update-LambdaCode -FunctionName $ParentLambdaName -SourceFile (Join-Path $SrcDir "parent_lambda.py")
}

if ($UpdateChildLambda) {
    Update-LambdaCode -FunctionName $ChildLambdaName -SourceFile (Join-Path $SrcDir "child_lambda.py")
}

if ($UpdateFilterLambda) {
    Update-LambdaCode -FunctionName $FilterLambdaName -SourceFile (Join-Path $SrcDir "child_output_filter_lambda.py")
}

Write-Host ""
Write-Host "Update complete."

if (Test-Path $TmpDir) {
    Remove-Item -Recurse -Force $TmpDir
}
