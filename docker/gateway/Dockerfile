FROM python:3.10-alpine

WORKDIR /opt/gateway

ADD . .
ENV PYTHONPATH=/opt/gateway

RUN cd gatewayn && pip install -r requirements.txt

CMD python demos/demo_gateway.py