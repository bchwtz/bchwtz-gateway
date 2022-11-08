FROM alpine:latest
ARG TARGETPLATFORM
RUN env > /.env
RUN apk update
RUN apk add libc6-compat
ADD gw-dumper-$(${TARGETPLATFORM} | grep -ohE [0-9a-zA-Z]+$) dumper
RUN chmod +x dumper
RUN mv dumper /usr/bin/

CMD env > /.env && dumper