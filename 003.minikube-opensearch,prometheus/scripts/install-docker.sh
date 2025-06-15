#!/bin/bash

echo "install docker"

sudo yum install -y docker
sudo systemctl enable --now docker.service
sudo usermod -a -G docker ec2-user