param(
    [switch]$IncludeDependencies
)

$ErrorActionPreference = "Stop"

$LAYER_DIR = "layer"
$PYTHON_DIR = "$LAYER_DIR\python"

if (Test-Path $LAYER_DIR) {
    Remove-Item -Recurse -Force $LAYER_DIR
}

New-Item -ItemType Directory -Path $PYTHON_DIR -Force | Out-Null

if ($IncludeDependencies) {
    Write-Host "Installing dependencies from requirements-layer.txt..." -ForegroundColor Yellow
    pip install -r requirements-layer.txt -t $PYTHON_DIR
} else {
    Write-Host "Skipping dependency installation (use -IncludeDependencies to install)" -ForegroundColor Yellow
}

Copy-Item scripts\custom_utils.py -Destination $PYTHON_DIR\

Compress-Archive -Path "$LAYER_DIR\*" -DestinationPath "dependencies-layer.zip" -Force
