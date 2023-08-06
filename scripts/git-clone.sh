#!/bin/bash -ex

echo "install git"
sudo yum install -y git

echo "git clone"
if [[ -z ${COMMIT_ID} ]]; then
  COMMIT_ID=main
fi
cd /tmp
git clone https://github.com/kohei39san/mystudy-handson.git
cd mystudy-handson
git checkout ${COMMIT_ID}
git submodule update --init
chmod -R +x scripts
