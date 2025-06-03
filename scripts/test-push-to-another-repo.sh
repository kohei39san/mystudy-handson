#!/bin/bash
# Test script for pushing to another repository

# Exit on error
set -e

# Check if required environment variables are set
if [ -z "$TARGET_REPO_PAT" ] || [ -z "$TARGET_REPO_OWNER" ] || [ -z "$TARGET_REPO_NAME" ]; then
    echo "Error: Required environment variables not set."
    echo "Please set the following environment variables:"
    echo "  TARGET_REPO_PAT: GitHub Personal Access Token"
    echo "  TARGET_REPO_OWNER: Target repository owner"
    echo "  TARGET_REPO_NAME: Target repository name"
    exit 1
fi

# Set up Git configuration
git config --global user.name "Test Script"
git config --global user.email "test@example.com"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Clone target repository
echo "Cloning target repository..."
git clone https://${TARGET_REPO_PAT}@github.com/${TARGET_REPO_OWNER}/${TARGET_REPO_NAME}.git $TEMP_DIR/target_repo

# Verify the owner of the target repository
echo "Verifying repository owner..."
REPO_OWNER=$(curl -s -H "Authorization: token $TARGET_REPO_PAT" \
  https://api.github.com/repos/$TARGET_REPO_OWNER/$TARGET_REPO_NAME | jq -r '.owner.login')

if [ "$REPO_OWNER" != "$TARGET_REPO_OWNER" ]; then
  echo "Error: Target repository owner does not match the expected owner"
  exit 1
fi

# Create new branch in target repository
echo "Creating new branch in target repository..."
cd $TEMP_DIR/target_repo
BRANCH_NAME="test-branch-$(date +%Y%m%d%H%M%S)"
git checkout -b $BRANCH_NAME

# Copy content from source to target
echo "Copying content from source to target..."
# Remove everything except .git directory from target repo
find . -mindepth 1 -not -path "./.git*" -delete

# Copy everything except .git directory from source repo to target repo
rsync -av --exclude='.git/' --exclude='target_repo/' $(pwd)/../../* ./

# Commit and push changes to target repository
echo "Committing and pushing changes..."
git add .
git commit -m "Test commit from script"
git push origin $BRANCH_NAME

# Create pull request in target repository
echo "Creating pull request..."
if command -v gh &> /dev/null; then
    gh auth login --with-token <<< "$TARGET_REPO_PAT"
    gh pr create \
      --repo $TARGET_REPO_OWNER/$TARGET_REPO_NAME \
      --base main \
      --head $BRANCH_NAME \
      --title "Test PR from script" \
      --body "This is a test pull request created by the test script."
else
    echo "GitHub CLI (gh) not found. Skipping pull request creation."
    echo "To create a pull request manually, visit:"
    echo "https://github.com/$TARGET_REPO_OWNER/$TARGET_REPO_NAME/compare/main...$BRANCH_NAME"
fi

# Clean up
echo "Cleaning up..."
rm -rf $TEMP_DIR

echo "Test completed successfully!"
echo "Branch created: $BRANCH_NAME"