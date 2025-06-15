#!/bin/bash
sudo rpm -Uvh http://repo.zabbix.com/zabbix/6.0/rhel/8/x86_64/zabbix-release-6.0-1.el8.noarch.rpm
sudo dnf -y install zabbix-agent
sudo systemctl enable zabbix-agent --now
systemctl status zabbix-agent --no-pager