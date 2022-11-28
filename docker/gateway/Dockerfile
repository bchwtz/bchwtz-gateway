FROM ghcr.io/bchwtz/bchwtz-gateway/ble-gateway-base:main

WORKDIR /opt/gateway

ADD . .
ADD ./docker/gateway/entrypoint.sh entrypoint.sh
ENV PYTHONPATH=/opt/gateway

ENTRYPOINT bash entrypoint.sh