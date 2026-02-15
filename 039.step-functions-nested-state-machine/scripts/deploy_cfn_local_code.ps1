param(
    [string]$StackName = "nested-sfn-study-dev",
    [string]$Region = "ap-northeast-1",
    [string]$Profile = ""
)

$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $PSScriptRoot
$TemplateFile = Join-Path $ProjectDir "cfn\infrastructure.yaml"

$AwsArgs = @()
if ($Profile -and $Profile.Trim().Length -gt 0) {
    $AwsArgs += @("--profile", $Profile)
}
$AwsArgs += @("--region", $Region)

Write-Host "===== CloudFormation Deploy (Local src/asl) ====="
Write-Host "Project Dir: $ProjectDir"
Write-Host "Stack Name : $StackName"
Write-Host "Region     : $Region"
Write-Host ""

function Invoke-AwsCommand {
    param(
        [string[]]$Command
    )

    $prevErrorAction = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    $prevNativePref = $null
    if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -Scope Global -ErrorAction SilentlyContinue) {
        $prevNativePref = $global:PSNativeCommandUseErrorActionPreference
        $global:PSNativeCommandUseErrorActionPreference = $false
    }
    $output = (& aws @Command 2>&1 | ForEach-Object { $_.ToString() }) -join "`n"
    $exitCode = $LASTEXITCODE
    if ($null -ne $prevNativePref) {
        $global:PSNativeCommandUseErrorActionPreference = $prevNativePref
    }
    $ErrorActionPreference = $prevErrorAction
    return [PSCustomObject]@{
        Output = $output
        ExitCode = $exitCode
    }
}

function Get-IndentedBlock($content, $indent) {
    $lines = $content -split "`r?`n"
    $prefix = " " * $indent
    return ($lines | ForEach-Object { "$prefix$_" }) -join "`n"
}

function Update-LiteralBlockInResource {
    param(
        [string[]]$Lines,
        [string]$ResourceName,
        [string]$KeyPattern,
        [string]$NewContent
    )

    $result = New-Object System.Collections.Generic.List[string]
    $currentResource = ""
    $i = 0
    while ($i -lt $Lines.Count) {
        $line = $Lines[$i]

        if ($line -match "^\s{2}([A-Za-z0-9]+):\s*$") {
            $currentResource = $Matches[1]
        }

        if ($currentResource -eq $ResourceName -and $line -match $KeyPattern) {
            $result.Add($line)
            $baseIndent = ($line -match "^(\s*)") | Out-Null
            $baseIndent = $Matches[1].Length
            $blockIndent = $baseIndent + 2
            $result.Add((Get-IndentedBlock -content $NewContent -indent $blockIndent))

            $i++
            while ($i -lt $Lines.Count) {
                $nextLine = $Lines[$i]
                $nextIndent = ($nextLine -match "^(\s*)") | Out-Null
                $nextIndent = $Matches[1].Length
                if ($nextLine.Trim().Length -eq 0) {
                    $i++
                    continue
                }
                if ($nextIndent -le $baseIndent) {
                    break
                }
                $i++
            }
            continue
        }

        $result.Add($line)
        $i++
    }

    return $result.ToArray()
}

function Load-AslWithCfnRefs {
    param(
        [string]$Path
    )

    $raw = Get-Content -Path $Path -Raw
    $raw = $raw.Replace('${parent_lambda_function_arn}', "${ParentLambdaFunction.Arn}")
    $raw = $raw.Replace('${child_state_machine_arn}', "${ChildStateMachine}")
    $raw = $raw.Replace('${child_output_filter_lambda_arn}', "${ChildOutputFilterLambdaFunction.Arn}")
    $raw = $raw.Replace('${child_lambda_function_arn}', "${ChildLambdaFunction.Arn}")
    return $raw.Trim()
}

Write-Host "Validating CloudFormation template..."
$validateResult = Invoke-AwsCommand -Command (@(
    "cloudformation", "validate-template",
    "--template-body", "file://$TemplateFile"
) + $AwsArgs)
if ($validateResult.ExitCode -ne 0) {
    throw ($validateResult.Output | Out-String)
}

$StackExists = $false
$describeResult = Invoke-AwsCommand -Command (@(
    "cloudformation", "describe-stacks",
    "--stack-name", $StackName
) + $AwsArgs)
if ($describeResult.ExitCode -eq 0) {
    $StackExists = $true
}

if ($StackExists) {
    Write-Host "Stack exists. Skipping stack update and moving to resource update."
} else {
    Write-Host "Creating stack..."
    $createResult = Invoke-AwsCommand -Command (@(
        "cloudformation", "create-stack",
        "--stack-name", $StackName,
        "--template-body", "file://$TemplateFile",
        "--capabilities", "CAPABILITY_NAMED_IAM"
    ) + $AwsArgs)
    if ($createResult.ExitCode -ne 0) {
        throw ($createResult.Output | Out-String)
    }
    Write-Host "Waiting for stack creation to complete..."
    $waitCreateResult = Invoke-AwsCommand -Command (@(
        "cloudformation", "wait", "stack-create-complete",
        "--stack-name", $StackName
    ) + $AwsArgs)
    if ($waitCreateResult.ExitCode -ne 0) {
        throw ($waitCreateResult.Output | Out-String)
    }
}

Write-Host ""
Write-Host "Fetching stack outputs..."
$outputResult = Invoke-AwsCommand -Command (@(
    "cloudformation", "describe-stacks",
    "--stack-name", $StackName,
    "--query", "Stacks[0].Outputs",
    "--output", "table"
) + $AwsArgs)
if ($outputResult.ExitCode -ne 0) {
    throw ($outputResult.Output | Out-String)
}

Write-Host ""
Write-Host "Updating resources from local src/asl..."
& (Join-Path $PSScriptRoot "update_resources_from_local.ps1") -StackName $StackName -Region $Region -Profile $Profile
