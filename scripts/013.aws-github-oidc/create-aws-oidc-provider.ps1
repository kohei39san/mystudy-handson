aws cloudformation deploy `
  --template-file ../../013.aws-github-oidc/template.yaml `
  --stack-name $args[0] `
  --capabilities CAPABILITY_NAMED_IAM `
  --parameter-overrides `
    GitHubRepository=$($args[1])

#ex. PowerShell -ExecutionPolicy RemoteSigned './create-aws-oidc-provider.ps1 stack-name "repo:github_username/repo_name:ref:refs/heads/main"'