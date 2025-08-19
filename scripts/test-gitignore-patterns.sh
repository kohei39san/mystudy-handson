#!/bin/bash

# Test script to validate .gitignore patterns for super-linter output files
# This script creates test files and verifies they are properly ignored by git

set -e

echo "Testing .gitignore patterns for super-linter output files..."

# Create test directories and files that should be ignored
mkdir -p super-linter-output
mkdir -p .super-linter-output
touch super-linter-output/super-linter-summary.md
touch super-linter-output/test-file.log
touch .super-linter-output/hidden-summary.md
touch super-linter.log
touch .super-linter.log

echo "Created test files:"
echo "- super-linter-output/super-linter-summary.md"
echo "- super-linter-output/test-file.log"
echo "- .super-linter-output/hidden-summary.md"
echo "- super-linter.log"
echo "- .super-linter.log"

# Check git status to see if files are ignored
echo ""
echo "Checking git status..."
untracked_files=$(git status --porcelain | grep '^??' | cut -c4- | grep -E '(super-linter|\.super-linter)' || true)

if [ -z "$untracked_files" ]; then
    echo "✅ SUCCESS: All super-linter output files are properly ignored by git"
    exit_code=0
else
    echo "❌ FAILURE: The following super-linter files are not ignored:"
    echo "$untracked_files"
    exit_code=1
fi

# Clean up test files
echo ""
echo "Cleaning up test files..."
rm -rf super-linter-output .super-linter-output super-linter.log .super-linter.log

echo "Test completed."
exit $exit_code