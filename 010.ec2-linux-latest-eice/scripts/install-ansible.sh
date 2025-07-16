#!/bin/bash

sudo dnf install python3.12 -y
python3 -m ensurepip --default-pip
pip install --user ansible
ansible localhost -m ping