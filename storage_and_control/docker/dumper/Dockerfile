FROM alpine:latest
RUN env > /.env
ADD gw-dumper /usr/bin/dumper

CMD env > /.env && /usr/bin/dumper