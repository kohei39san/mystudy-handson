# Setup script for GitHub Actions repository configuration

# Function to check if gh CLI is installed
function Test-GhCliInstalled {
    try {
        $null = gh --version
        return $true
    }
    catch {
        Write-Error "GitHub CLI (gh) is not installed. Please install it first: https://cli.github.com/"
        return $false
    }
}

# Function to get repository name from git config
function Get-RepositoryName {
    try {
        # Get the remote URL
        $remoteUrl = git config --get remote.origin.url
        
        # Extract owner/repo from different URL formats
        if ($remoteUrl -match "github\.com[:/]([^/]+)/([^/.]+)") {
            return "$($Matches[1])/$($Matches[2])"
        }
        throw "Could not determine repository name from git config"
    }
    catch {
        Write-Error "Failed to get repository name: $_"
        exit 1
    }
}

# Function to setup repository permissions
function Set-GithubActionsPermissions {
    param(
        [string]$RepoName
    )
    
    Write-Host "Setting up GitHub Actions permissions for $RepoName..."
    
    # Enable GitHub Actions for the repository
    gh api --method PUT "/repos/$RepoName/actions/permissions" `
        --field enabled=true
    
    # Set repository permissions for OIDC
    gh api --method PUT "/repos/$RepoName/actions/permissions" `
        --field allowed_actions="all" `
        --field can_approve_pull_request_reviews=false

    # Enable ID token permissions for OIDC
    gh api --method PUT "/repos/$RepoName/actions/permissions/id-token" `
        --field enabled=true
}

# Function to set repository secrets
function Set-RepositorySecrets {
    param(
        [string]$RepoName
    )
    
    Write-Host "Setting up repository secrets..."
    
    # Define all secrets to be set
    $secretsToSet = @(
        @{Name="AWS_ROLE_ARN"; Prompt="Enter AWS Role ARN"},
        @{Name="GEMINI_API_KEY"; Prompt="Enter Gemini API Key"},
        @{Name="LLM_API_KEY"; Prompt="Enter LLM API Key"},
        @{Name="LLM_BASE_URL"; Prompt="Enter LLM Base URL"},
        @{Name="PAT_TOKEN"; Prompt="Enter GitHub PAT Token"},
        @{Name="PAT_USERNAME"; Prompt="Enter GitHub PAT Username"}
    )

    foreach ($secret in $secretsToSet) {
        $secretValue = Read-Host -Prompt $secret.Prompt -AsSecureString
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secretValue)
        $secretValueText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
        gh secret set $secret.Name --body $secretValueText --repo $RepoName
    }
}

# Function to set repository variables
function Set-RepositoryVariables {
    param(
        [string]$RepoName
    )
    
    Write-Host "Setting up repository variables..."
    
    # Set LLM_MODEL variable
    $llmModel = Read-Host -Prompt "Enter LLM Model name"
    gh variable set LLM_MODEL --body $llmModel --repo $RepoName
}

# Main execution
Write-Host "Starting GitHub Actions repository setup..."

# Check prerequisites
if (-not (Test-GhCliInstalled)) {
    exit 1
}

# Verify GitHub authentication
try {
    $null = gh auth status
}
catch {
    Write-Error "Not authenticated with GitHub. Please run 'gh auth login' first."
    exit 1
}

# Get repository name
$repoName = Get-RepositoryName
Write-Host "Detected repository: $repoName"

# Setup GitHub Actions permissions
try {
    Set-GithubActionsPermissions -RepoName $repoName
    Write-Host "Successfully configured GitHub Actions permissions."
}
catch {
    Write-Error "Failed to set GitHub Actions permissions: $_"
    exit 1
}

# Setup repository secrets
try {
    Set-RepositorySecrets -RepoName $repoName
    Write-Host "Successfully set repository secrets."
}
catch {
    Write-Error "Failed to set repository secrets: $_"
    exit 1
}

# Setup repository variables
try {
    Set-RepositoryVariables -RepoName $repoName
    Write-Host "Successfully set repository variables."
}
catch {
    Write-Error "Failed to set repository variables: $_"
    exit 1
}

Write-Host "`nSetup completed successfully!"
Write-Host "Required configurations:"
Write-Host "1. Ensure AWS OIDC provider is configured for GitHub Actions"
Write-Host "2. Verify the IAM role permissions are correctly set"
Write-Host "3. Check workflow files in .github/workflows/ for any specific requirements"
