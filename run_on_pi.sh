#!/bin/bash
cd deployments/gateway
docker-compose --env-file ../../.env -f docker-compose.yml -f docker-compose.rpi.yml up -d
