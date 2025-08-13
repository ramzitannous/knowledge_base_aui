FROM ubuntu:latest
LABEL authors="myadmin"

ENTRYPOINT ["top", "-b"]