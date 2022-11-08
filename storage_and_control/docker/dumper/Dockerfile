FROM alpine:latest
RUN env > /.env
ADD gw-dumper /usr/bin/dumper
RUN chmod +x /usr/bin/dumper

CMD env > /.env && dumper