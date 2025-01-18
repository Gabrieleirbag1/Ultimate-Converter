#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")

docker run -d \
  --name=inkscape \
  --security-opt seccomp=unconfined `#optional` \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Etc/UTC \
  -p 3000:3000 \
  -p 3001:3001 \
  -v "$SCRIPT_DIR:$SCRIPT_DIR" -w "$SCRIPT_DIR" \
  --restart unless-stopped \
  lscr.io/linuxserver/inkscape:latest