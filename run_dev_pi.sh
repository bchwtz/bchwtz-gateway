#!/bin/bash
# This script is intended to run on a raspberry pi to start the gateway microservices cluster - everything is going to run inside docker
if [ ! -f .env ]
then
    echo "env did not exist, will copy sample values!"
    cp .env-default .env
fi
cd deployments/gateway
docker compose --env-file ../../.env -f docker-compose.dev-rpi.yml up -d