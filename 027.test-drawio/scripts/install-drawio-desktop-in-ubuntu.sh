#!/bin/bash

apt-get update
apt-get install -y xvfb wget libasound2t64
wget -O /tmp/drawio.deb https://github.com/jgraph/drawio-desktop/releases/download/v28.0.6/drawio-amd64-28.0.6.deb
apt-get install -y /tmp/drawio.deb 
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS=unix:path=$XDG_RUNTIME_DIR/bus
/etc/init.d/dbus start
dbus-daemon --session --address=$DBUS_SESSION_BUS_ADDRESS --fork