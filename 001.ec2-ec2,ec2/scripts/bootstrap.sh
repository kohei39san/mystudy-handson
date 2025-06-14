#!/bin/bash

sudo groupadd -g 10000 testgroup
sudo useradd -d /home/testuser1 -g testgroup -u 10001 testuser1
sudo mkdir /home/testuser1/.ssh
sudo cp ~/.ssh/authorized_keys /home/testuser1/.ssh/authorized_keys
sudo chmod og-rwx /home/testuser1/.ssh
sudo chown -R testuser1:testgroup /home/testuser1/.ssh
sudo gpasswd -a testuser1 wheel
echo -n "testuser1" | sudo passwd --stdin testuser1
sudo chage testuser1 -M 50

sudo useradd -d /home/testuser2 -g testgroup -u 10002 testuser2
sudo mkdir /home/testuser2/.ssh
sudo cp ~/.ssh/authorized_keys /home/testuser2/.ssh/authorized_keys
sudo chmod og-rwx /home/testuser2/.ssh
sudo chown -R testuser2:testgroup /home/testuser2/.ssh
sudo gpasswd -a testuser2 wheel
echo -n "testuser2" | sudo passwd --stdin testuser2
sudo chage testuser2 -M 50

sudo sed -i '8s/$/minlen=8 dcredit=-2 ucredit=-2 lcredit=-2 ocredit=-2/' /etc/pam.d/system-auth
sudo sed -i '9i password    requisite     pam_pwquality.so remember=6 enforce_for_root' /etc/pam.d/system-auth
sudo sed -i '5i auth        required      pam_tally2.so deny=5 unlock_time=0' /etc/pam.d/password-auth