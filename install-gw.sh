#!/bin/sh

BINARY_PATH=/usr/bin/
BINARY_NAME=gw
DIST_DIR=autoinstall
MONGO_PASSW=$(openssl rand -base64 24 | sed -e 's/\///g')
MQTT_PASSW=$(openssl rand -base64 24 | sed -e 's/\///g')

if [ -f $BINARY_PATH$BINARY_NAME ]; then
    echo "executable $BINARY_PATH$BINARY_NAME already exists - aborting installation"
    exit
fi
sudo apt update && sudo apt install -y docker.io docker-compose
if [ ! -d $DIST_DIR ]; then
    mkdir -p $DIST_DIR
    cd $DIST_DIR
    wget https://bchwtz.github.io/bchwtz-gateway/dist/gw-arm64
    wget https://bchwtz.github.io/bchwtz-gateway/dist/docker-compose.yml
    wget https://bchwtz.github.io/bchwtz-gateway/dist/docker-compose.rpi.yml
    wget https://bchwtz.github.io/bchwtz-gateway/dist/.env-default
    wget https://bchwtz.github.io/bchwtz-gateway/dist/uninstall-gw.sh
    mv docker-compose.yml docker-compose.std.yml
    sed -i -e 's/image: mongo$/image: apcheamitru\/arm32v7-mongo/' docker-compose.yml
    chmod +x uninstall-gw.sh
fi
if [ -f .env-default ]
then
    echo "configuring auto-load of env-variables"
    awk '!/^$/{print "export " $0}' .env-default | sed -e 's/\(MQTT_PASSWORD=\).*/\1"'$MQTT_PASSW'"/g' | sed -e 's/\(MONGO_PASSWORD=\).*/\1"'$MONGO_PASSW'"/g' > gateway-vars.sh
    . $(pwd)/gateway-vars.sh
    sudo cp gateway-vars.sh /etc/profile.d/
    sudo mv $(pwd)/gw-arm64 $BINARY_PATH$BINARY_NAME
    mv .env-default .env
fi
echo "generating docker-compose"
docker-compose --project-name gateway -f docker-compose.std.yml -f docker-compose.rpi.yml config > docker-compose.yml
rm docker-compose.std.yml docker-compose.rpi.yml
docker-compose up