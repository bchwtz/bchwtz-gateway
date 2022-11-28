#!/bin/bash

docker-compose down
cd ..
rm -rf autoinstall
sudo rm -rf /usr/bin/gw
sudo rm -rf /etc/profile.d/gateway-vars.sh