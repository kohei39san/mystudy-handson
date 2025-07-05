# PowerShell script to run the Python script for updating markdown files

# Change to the repository root directory
Set-Location -Path $PSScriptRoot\..

# Run the Python script
python scripts\update_markdown_files.py