#!/bin/bash

python3 -m ensurepip --default-pip
pip install --user ansible
ansible localhost -m ping