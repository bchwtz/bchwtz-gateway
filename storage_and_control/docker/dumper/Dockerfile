FROM alpine:latest
ARG TARGETARCH
RUN env > /.env
RUN apk update
RUN apk add libc6-compat
ADD gw-dumper-${TARGETARCH} dumper
RUN chmod +x dumper
RUN mv dumper /usr/bin/

CMD env > /.env && dumper