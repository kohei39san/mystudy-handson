#!/bin/bash -ex

echo 'install docker'
if [[ -z ${DOCKER_VERSION} ]]; then
  DOCKER_VERSION="25.0.3"
fi
sudo yum install -y docker-${DOCKER_VERSION}
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $(whoami)

echo "install docker-compose"
if [[ -z ${DOCKER_COMPOSE_VERSION} ]];then
  DOCKER_COMPOSE_VERSION="v2.24.6"
fi
sudo curl -SL https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
#echo 'alias dk="docker-compose"' >> ~/.bash_profile
