FROM alpine:latest
RUN env > /.env
ADD build-artifacts/dumper /usr/bin/dumper

CMD /usr/bin/dumper