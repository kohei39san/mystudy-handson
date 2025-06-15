# Check if stack exists
$stackName = $args[0]
$stackExists = $false

try {
    aws cloudformation describe-stacks --stack-name $stackName | Out-Null
    $stackExists = $true
    Write-Host "Stack '$stackName' exists."
} catch {
    Write-Host "Stack '$stackName' does not exist."
}

# If stack exists, delete it and wait for completion
if ($stackExists) {
    Write-Host "Deleting stack '$stackName'..."
    aws cloudformation delete-stack --stack-name $stackName
    
    Write-Host "Waiting for stack deletion to complete..."
    aws cloudformation wait stack-delete-complete --stack-name $stackName
    Write-Host "Stack deletion completed."
}

Write-Host "Creating new stack '$stackName'..."
aws cloudformation deploy `
  --template-file ../src/cfn/template.yaml `
  --stack-name $args[0] `
  --capabilities CAPABILITY_NAMED_IAM `
  --parameter-overrides `
    GitHubRepository=$($args[1])

#ex. PowerShell -ExecutionPolicy RemoteSigned './create-aws-oidc-provider.ps1 stack-name "repo:github_username/repo_name:ref:refs/heads/main"'