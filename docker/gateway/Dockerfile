FROM python:3.10

WORKDIR /opt/gateway

ADD . .
ADD ./docker/gateway/entrypoint.sh entrypoint.sh
ENV PYTHONPATH=/opt/gateway

RUN apt-get update -y
RUN apt-get install -y bluez bluetooth

RUN pip install -r requirements.txt

ENTRYPOINT bash entrypoint.sh