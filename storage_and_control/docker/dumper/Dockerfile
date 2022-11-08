FROM alpine:latest
ARG TARGETPLATFORM
RUN env > /.env
RUN apk update
RUN apk add libc6-compat
RUN export ARCH=$(${TARGETPLATFORM} | grep -ohE [0-9a-zA-Z]+$)
ADD gw-dumper-${ARCH} dumper
RUN chmod +x dumper
RUN mv dumper /usr/bin/

CMD env > /.env && dumper