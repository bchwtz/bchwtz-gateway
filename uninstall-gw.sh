#!/bin/bash

docker-compose down
cd ..
rm -rf gateway-autoinstall
sudo rm -f /usr/bin/gw
sudo rm -f /etc/profile.d/gateway-vars.sh