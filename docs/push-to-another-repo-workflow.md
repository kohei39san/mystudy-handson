# Push to Another Repository Workflow

This document explains how to use the "Push to Another Repository" GitHub Actions workflow.

## Overview

This workflow allows you to push the content of the main branch to another repository that you own and create a pull request in that repository. This is useful for syncing changes between repositories or deploying content from one repository to another.

## Prerequisites

Before using this workflow, you need to set up the following secrets in your GitHub repository:

1. `TARGET_REPO_PAT`: A GitHub Personal Access Token (PAT) with permissions to push to the target repository and create pull requests. The token should have the following permissions:
   - `repo` (Full control of private repositories)
   - `workflow` (if you need to trigger workflows in the target repository)

2. `TARGET_REPO_OWNER`: The GitHub username or organization name that owns the target repository.

3. `TARGET_REPO_NAME`: The name of the target repository.

## How to Create a Personal Access Token (PAT)

1. Go to your GitHub account settings
2. Click on "Developer settings" in the left sidebar
3. Click on "Personal access tokens" and then "Tokens (classic)"
4. Click "Generate new token" and select "Generate new token (classic)"
5. Give your token a descriptive name
6. Select the necessary scopes (at minimum, select the `repo` scope)
7. Click "Generate token"
8. Copy the token immediately (you won't be able to see it again)

## How to Add Secrets to Your Repository

1. Go to your repository on GitHub
2. Click on "Settings"
3. Click on "Secrets and variables" in the left sidebar, then "Actions"
4. Click "New repository secret"
5. Add each of the required secrets mentioned above

## Using the Workflow

The workflow is triggered manually. To run it:

1. Go to the "Actions" tab in your repository
2. Select the "Push to Another Repository" workflow
3. Click "Run workflow"
4. Fill in the following parameters:
   - **Branch name**: The name of the branch to create in the target repository
   - **Commit message**: The message for the commit in the target repository
   - **PR title**: The title for the pull request
   - **PR body**: The description for the pull request
5. Click "Run workflow"

## Testing Locally

A test script is provided to verify the functionality locally before running the GitHub Actions workflow:

```bash
# Make the script executable
chmod +x scripts/test-push-to-another-repo.sh

# Set the required environment variables
export TARGET_REPO_PAT="your-personal-access-token"
export TARGET_REPO_OWNER="target-repo-owner"
export TARGET_REPO_NAME="target-repo-name"

# Run the test script
./scripts/test-push-to-another-repo.sh
```

The test script will:
1. Clone the target repository
2. Create a new branch
3. Copy the content from your local repository to the target repository
4. Commit and push the changes
5. Create a pull request (if GitHub CLI is installed)

## Security Considerations

- The workflow verifies that the target repository belongs to the specified owner before pushing any changes.
- Use a dedicated PAT with the minimum required permissions.
- Regularly rotate your PAT for security.

## Troubleshooting

If the workflow fails, check the following:

1. Ensure all required secrets are correctly set up
2. Verify that the PAT has the necessary permissions
3. Confirm that the target repository exists and is accessible with the provided PAT
4. Check that the target repository owner matches the value in `TARGET_REPO_OWNER`