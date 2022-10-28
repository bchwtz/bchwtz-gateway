FROM python:3.10

WORKDIR /opt/gateway

ADD . .
ENV PYTHONPATH=/opt/gateway

RUN pip install -r requirements.txt

CMD env > .env && python demos/demo_gateway.py