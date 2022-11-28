#!/bin/sh

BINARY_PATH=/usr/bin/
BINARY_NAME=gw

if [ -f $BINARY_PATH$BINARY_NAME ]; then
    echo "executable $BINARY_PATH$BINARY_NAME already exists - aborting installation"
    exit
fi
sudo apt update && sudo apt install docker-ce docker-compose
mkdir -p autoinstall
cd autoinstall
wget https://bchwtz.github.io/bchwtz-gateway/dist/gw-arm64
wget https://bchwtz.github.io/bchwtz-gateway/dist/docker-compose.yml
wget https://bchwtz.github.io/bchwtz-gateway/dist/docker-compose.rpi.yml
mv docker-compose.yml docker-compose.std.yml
wget https://bchwtz.github.io/bchwtz-gateway/dist/.env-default
if [ -f ../.env-default ]
then
  export $(cat ../.env-default | xargs)
fi
# sudo mv gw-arm64 /usr/bin/gw
docker-compose -f docker-compose.std.yml -f docker-compose.rpi.yml config > docker-compose.yml