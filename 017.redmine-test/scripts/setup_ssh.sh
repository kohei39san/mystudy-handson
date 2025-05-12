#!/bin/bash
mkdir -p .ssh
touch .ssh/id_rsa.pub
touch .ssh/id_rsa
chmod 700 .ssh
chmod 600 .ssh/id_rsa*

# Generate a new SSH key pair for CI environment
ssh-keygen -t rsa -b 2048 -f .ssh/id_rsa -N ""