param(
    [Parameter(Mandatory=$true)]
    [string]$CompartmentId,
    
    [Parameter(Mandatory=$true)]
    [string]$StackName,
    
    [string]$ZipFile = "../src/terraform-config.zip",
    
    [string]$BucketName = "terraform-state-bucket"
)

$ErrorActionPreference = "Stop"

Write-Host "Creating OCI Resource Manager stack..." -ForegroundColor Green

# Create stack
$stackId = oci resource-manager stack create `
    --compartment-id $CompartmentId `
    --display-name $StackName `
    --description "Terraform state bucket for OCI" `
    --config-source $ZipFile `
    --variables "{\"compartment_id\":\"$CompartmentId\",\"bucket_name\":\"$BucketName\"}" `
    --query "data.id" --raw-output

Write-Host "Stack created with ID: $stackId" -ForegroundColor Yellow

Write-Host "Creating plan job..." -ForegroundColor Green

# Create plan job
$planJobId = oci resource-manager job create-plan-job `
    --stack-id $stackId `
    --query "data.id" --raw-output

Write-Host "Plan job created with ID: $planJobId" -ForegroundColor Yellow
Write-Host "Waiting for plan to complete..." -ForegroundColor Green

# Wait for plan to complete
do {
    Start-Sleep -Seconds 10
    $planStatus = oci resource-manager job get --job-id $planJobId --query "data.lifecycle-state" --raw-output
    Write-Host "Plan status: $planStatus" -ForegroundColor Cyan
} while ($planStatus -eq "IN_PROGRESS")

if ($planStatus -ne "SUCCEEDED") {
    Write-Error "Plan failed with status: $planStatus"
    exit 1
}

Write-Host "Creating apply job..." -ForegroundColor Green

# Create apply job
$applyJobId = oci resource-manager job create-apply-job `
    --stack-id $stackId `
    --execution-plan-strategy "FROM_PLAN_JOB_ID" `
    --execution-plan-job-id $planJobId `
    --query "data.id" --raw-output

Write-Host "Apply job created with ID: $applyJobId" -ForegroundColor Yellow
Write-Host "Waiting for apply to complete..." -ForegroundColor Green

# Wait for apply to complete
do {
    Start-Sleep -Seconds 15
    $applyStatus = oci resource-manager job get --job-id $applyJobId --query "data.lifecycle-state" --raw-output
    Write-Host "Apply status: $applyStatus" -ForegroundColor Cyan
} while ($applyStatus -eq "IN_PROGRESS")

if ($applyStatus -eq "SUCCEEDED") {
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
    Write-Host "Stack ID: $stackId" -ForegroundColor Yellow
} else {
    Write-Error "Apply failed with status: $applyStatus"
    exit 1
}

Write-Host "Deployment completed. You can view the stack in OCI Console." -ForegroundColor Green