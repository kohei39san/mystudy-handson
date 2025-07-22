#!/bin/bash

sudo dnf install python3.12 -y
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 2
python3 -m ensurepip --default-pip
pip install --user ansible boto3
ansible localhost -m ping