#!/bin/bash -ex

echo "install git"
sudo yum install -y git

echo "git clone"
if [[ -z ${COMMIT_ID} ]]; then
  COMMIT_ID=main
fi
if [[ -z ${REPO_URL} ]];then
  REPO_URL="https://github.com/kohei39san/mystudy-handson.git"
fi
if [[ -z ${CLONE_DIR} ]]; then
  CLONE_DIR="/tmp"
fi
cd "${CLONE_DIR}"
git clone ${REPO_URL}
cd mystudy-handson
git checkout ${COMMIT_ID}
git submodule update --init
chmod -R +x scripts
