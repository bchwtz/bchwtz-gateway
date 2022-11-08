#!/bin/bash
# This script is intended to run on a raspberry pi to start the gateway microservices cluster - everything is going to run inside docker
if [ ! -f .env ]
then
    echo "env did not exist, will copy sample values!"
    cp .env-default .env
fi

export PATH=$PATH:$(pwd)/bin
cd deployments/gateway
docker-compose --env-file ../../.env -f docker-compose.yml -f docker-compose.rpi.yml pull
sudo killall -9 bluetoothd
docker-compose --env-file ../../.env -f docker-compose.yml -f docker-compose.rpi.yml up -d
