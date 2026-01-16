# Docker を使用してLinux用Lambda Layerを作成するスクリプト
# Amazon Linux 2023, Python 3.13対応

param(
    [string]$LayerName = "pydantic-psycopg2-layer",
    [string]$PythonVersion = "3.13"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Creating Linux-compatible Lambda Layer with Docker ===" -ForegroundColor Green
Write-Host "Layer Name: $LayerName"
Write-Host "Python Version: $PythonVersion"

# Check if Docker is available
try {
    docker --version | Out-Null
    Write-Host "Docker is available" -ForegroundColor Green
} catch {
    Write-Host "Docker is not available. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Create temporary directory for Docker build
$BuildDir = "docker-build"
if (Test-Path $BuildDir) {
    Remove-Item -Path $BuildDir -Recurse -Force
}
New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null

# Create Dockerfile
$DockerfileContent = @"
FROM public.ecr.aws/lambda/python:3.13

# Install pip dependencies to /opt/python
COPY requirements.txt .
RUN pip install -r requirements.txt -t /opt/python/

# Clean up unnecessary files
RUN find /opt/python -type d -name "__pycache__" -exec rm -rf {} + || true
RUN find /opt/python -name "*.pyc" -delete || true
RUN find /opt/python -name "*.pyo" -delete || true
RUN find /opt/python -name "*.dist-info" -exec rm -rf {} + || true
RUN find /opt/python -name "*.egg-info" -exec rm -rf {} + || true

# Set working directory
WORKDIR /opt
"@

$DockerfileContent | Out-File -FilePath "$BuildDir/Dockerfile" -Encoding UTF8

# Copy requirements.txt to build directory
Copy-Item "requirements.txt" "$BuildDir/requirements.txt"

# Build Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t lambda-layer-builder $BuildDir

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed" -ForegroundColor Red
    exit 1
}

# Create container and copy layer content
Write-Host "Extracting layer content..." -ForegroundColor Yellow
$ContainerId = docker create lambda-layer-builder

# Create target directory
$TargetDir = "lambda_layer_linux"
if (Test-Path $TargetDir) {
    Remove-Item -Path $TargetDir -Recurse -Force
}
New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

# Copy the python directory from container
docker cp "${ContainerId}:/opt/python" $TargetDir

# Clean up Docker container
docker rm $ContainerId

# Create layer structure
$LayerStructure = "lambda_layer_linux"
if (-not (Test-Path "$LayerStructure/python")) {
    Write-Host "Failed to extract layer content" -ForegroundColor Red
    exit 1
}

# Create ZIP file
Write-Host "Creating ZIP file..." -ForegroundColor Yellow
$ZipPath = "${LayerName}-linux.zip"
if (Test-Path $ZipPath) {
    Remove-Item -Path $ZipPath -Force
}

# Use PowerShell compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($LayerStructure, $ZipPath)

# Check file size
$LayerSize = (Get-Item $ZipPath).Length
$LayerSizeMB = [math]::Round($LayerSize / 1MB, 2)
Write-Host "Layer Size: $LayerSizeMB MB" -ForegroundColor Cyan

# AWS Lambda layer size limit check (50MB)
$MaxSizeBytes = 50 * 1MB
if ($LayerSize -gt $MaxSizeBytes) {
    Write-Host "WARNING: Layer size exceeds 50MB ($LayerSizeMB MB)" -ForegroundColor Red
    Write-Host "This layer may not be usable due to Lambda limits." -ForegroundColor Red
} else {
    Write-Host "Layer size is within limits ($LayerSizeMB MB)" -ForegroundColor Green
}

# Clean up temporary files
Remove-Item -Path $BuildDir -Recurse -Force
Remove-Item -Path $LayerStructure -Recurse -Force

Write-Host "=== Linux Lambda Layer Creation Complete ===" -ForegroundColor Green
Write-Host "Created file: $ZipPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "This layer is compatible with Lambda runtime: python3.13" -ForegroundColor Yellow
Write-Host "You can now use this ZIP file for Lambda layer deployment." -ForegroundColor White