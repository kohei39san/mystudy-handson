#!/bin/bash

sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker $(whoami)