#!/bin/bash -e

echo "get credentials for ec2..."
ACCOUNT_ID=`echo -n $(aws sts get-caller-identity | jq -r .Account)`
SSO_ACCESS_TOKEN=`echo -n $(grep -Eoh "\"accessToken\":[^,]+" -r ~/.aws/sso/cache/ | awk -F" " '{ print $2 }' | sed -e "s/\"//g")`
CREDENTIALS=$(aws sso get-role-credentials --role-name ${SSO_ROLE_NAME} --account-id ${ACCOUNT_ID} --access-token ${SSO_ACCESS_TOKEN})
ACCESS_KEY_ID=`echo -n $(echo "${CREDENTIALS}" | jq -r .roleCredentials.accessKeyId)`
SECRET_ACCESS_KEY=`echo -n $(echo "${CREDENTIALS}" | jq -r .roleCredentials.secretAccessKey)`
SESSION_TOKEN=`echo -n $(echo "${CREDENTIALS}" | jq -r .roleCredentials.sessionToken)`

echo "ssh ec2"
SSH_CMD="ssh -i ${PRIVATE_KEY} ${SSH_USER}@${INSTANCE_IP} AWS_ACCESS_KEY_ID=${ACCESS_KEY_ID} AWS_SECRET_ACCESS_KEY=${SECRET_ACCESS_KEY} AWS_SESSION_TOKEN=${SESSION_TOKEN} CLUSTER=${CLUSTER} KUBECTL_INSTALL_URL=${KUBECTL_INSTALL_URL} KUBECTL_SHA_INSTALL_URL=${KUBECTL_SHA_INSTALL_URL} KUBECTL_ROLE_ARN=${KUBECTL_ROLE_ARN} KUBECTL_GROUP='system:masters' KUBECTL_USERNAME='admin'"
aws ec2-instance-connect send-ssh-public-key --instance-id ${INSTANCE_ID} --instance-os-user ${SSH_USER} --ssh-public-key=file://${PUBLIC_KEY}
${SSH_CMD} /bin/bash -e << 'EOF'
echo "update awscli"
sudo yum remove awscli -y
sudo rm -rf /usr/local/aws-cli/
cd /tmp
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli

echo "install kubectl"
cd /tmp
curl -O ${KUBECTL_INSTALL_URL}
curl -O ${KUBECTL_SHA_INSTALL_URL}
sha256sum -c kubectl.sha256
chmod +x ./kubectl
sudo cp ./kubectl /usr/local/bin
echo 'alias k="kubectl"' >> "${HOME}/.bash_profile"
echo 'complete -F __start_kubectl k' >> "${HOME}/.bash_profile"
echo 'source <(kubectl completion bash)' >> "${HOME}/.bash_profile"

echo "install eksctl"
ARCH=amd64
PLATFORM=$(uname -s)_$ARCH
cd /tmp
curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"
curl -sL "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_checksums.txt" | grep $PLATFORM | sha256sum --check
tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp && rm eksctl_$PLATFORM.tar.gz
sudo mv /tmp/eksctl /usr/local/bin

echo "install others"
sudo yum install -y jq

echo "ec2 connecting eks..."
aws eks update-kubeconfig --name "${CLUSTER}"
REGION=`echo -n $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed -e s/.$//)`
while [ `echo -n $(eksctl get iamidentitymapping --cluster "${CLUSTER}" --region ${REGION} -o json | jq -r '.[0].username')` = "null" ];do
  echo "waiting aws-auth mapping ..."
  sleep 10
done
eksctl create iamidentitymapping --cluster "${CLUSTER}" --region "${REGION}" --arn "${KUBECTL_ROLE_ARN}" --username "${KUBECTL_USERNAME}" --group "${KUBECTL_GROUP}" --no-duplicate-arns
EOF
