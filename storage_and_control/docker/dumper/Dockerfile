FROM alpine:latest
ARG TARGETPLATFORM
RUN env > /.env
RUN apk update
RUN apk add libc6-compat
RUN export ARCH=$(grep \/.*$)
ADD gw-dumper-${ARCH} dumper
RUN chmod +x dumper
RUN mv dumper /usr/bin/

CMD env > /.env && dumper