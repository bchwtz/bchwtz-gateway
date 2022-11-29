#!/bin/sh

docker-compose down
bash $(pwd)/unset-gateway-vars.sh
cd ..
rm -rf gateway-autoinstall
sudo rm -f /usr/bin/gw
sudo rm -f /etc/profile.d/gateway-vars.sh