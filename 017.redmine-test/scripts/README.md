# Setup Scripts

This directory contains utility scripts used during the deployment process.

## setup_ssh.sh

This script is used to set up SSH keys in the CI/CD environment. It:

1. Creates the .ssh directory with proper permissions
2. Creates SSH key files
3. Generates a new SSH key pair for use with EC2 Instance Connect

The script is automatically executed during the Terraform initialization phase.