#!/bin/bash
sudo yum install -y amazon-cloudwatch-agent
sudo systemctl enable amazon-cloudwatch-agent.service
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s
sudo systemctl status amazon-cloudwatch-agent.service --no-pager