# AWS Systems Manager Session Manager Plugin Installation Script for Windows

Write-Host "Installing AWS Systems Manager Session Manager Plugin..." -ForegroundColor Green

# Download URL for Windows
$downloadUrl = "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPluginSetup.exe"
$installerPath = "$env:TEMP\SessionManagerPluginSetup.exe"

try {
    # Download the installer
    Write-Host "Downloading Session Manager Plugin..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath
    
    # Run the installer
    Write-Host "Running installer..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait
    
    # Verify installation
    Write-Host "Verifying installation..." -ForegroundColor Yellow
    $pluginPath = "${env:ProgramFiles}\Amazon\SessionManagerPlugin\bin\session-manager-plugin.exe"
    
    if (Test-Path $pluginPath) {
        Write-Host "✓ Session Manager Plugin installed successfully!" -ForegroundColor Green
        Write-Host "Plugin location: $pluginPath" -ForegroundColor Cyan
        
        # Test the plugin
        & $pluginPath
        Write-Host "✓ Plugin is working correctly!" -ForegroundColor Green
    } else {
        Write-Host "✗ Installation may have failed. Plugin not found at expected location." -ForegroundColor Red
    }
    
    # Clean up
    Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "✗ Error during installation: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Restart your PowerShell/Command Prompt" -ForegroundColor White
Write-Host "2. Try connecting to your EC2 instance again" -ForegroundColor White