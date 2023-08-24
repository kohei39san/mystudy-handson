#!/bin/bash -e

echo "install java"
sudo yum install java -y

echo "install jmeter"
if [[ -z ${JMETER_VERSION} ]];then
  JMETER_VERSION="5.6.2"
fi
mkdir /tmp/jmeter
cd /tmp/jmeter
wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz
tar -xzvf apache-jmeter-${JMETER_VERSION}.tgz
sudo mv apache-jmeter-${JMETER_VERSION} /opt/
sudo ln -s /opt/apache-jmeter-${JMETER_VERSION}/bin/jmeter /usr/local/bin/jmeter
