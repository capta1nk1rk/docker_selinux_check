#!/bin/bash
# Builds a fresh container from the current dir, then runs it
docker build . -t docker-selinux-check

docker run -it -v /etc/selinux:/etc/selinux -v /etc/hostname:/etc/nodehostname -p 5000:5000 docker-selinux-check:latest

