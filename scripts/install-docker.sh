#!/bin/bash -ex

echo 'install docker'
VERSION="20.10.17"
sudo yum install -y docker-${VERSION}
sudo systemctl start docker
sudo usermod -aG docker $(whoami)

echo "install docker-compose"
VERSION="v2.12.2"
sudo curl -SL https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
echo 'alias dk="docker-compose"' >> ~/.bash_profile
