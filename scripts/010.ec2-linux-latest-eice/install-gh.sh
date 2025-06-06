#!/bin/bash

sudo dnf install 'dnf-command(config-manager)'
sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install -y git
sudo dnf install gh --repo gh-cli -y
dnf --version
gh version