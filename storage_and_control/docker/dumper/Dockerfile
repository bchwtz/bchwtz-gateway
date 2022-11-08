FROM alpine:latest
ARG TARGETPLATFORM
RUN env > /.env
RUN apk update
RUN apk add libc6-compat
ADD gw-dumper-${TARGETPLATFORM} dumper
RUN chmod +x dumper
RUN mv dumper /usr/bin/

CMD env > /.env && dumper