param(
    [string]$OutputPath = "../src/terraform-config.zip"
)

$ErrorActionPreference = "Stop"

$TerraformDir = ".."
$TfFiles = Get-ChildItem -Path $TerraformDir -Filter "*.tf"

if ($TfFiles.Count -eq 0) {
    Write-Error "No .tf files found in $TerraformDir"
    exit 1
}

if (Test-Path $OutputPath) {
    Remove-Item $OutputPath -Force
}

Compress-Archive -Path "$TerraformDir\*.tf" -DestinationPath $OutputPath

Write-Host "Created zip file: $OutputPath" -ForegroundColor Green
Write-Host "Contains $($TfFiles.Count) .tf files:" -ForegroundColor Yellow
$TfFiles | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Cyan }