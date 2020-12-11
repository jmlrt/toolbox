FROM debian:10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y curl git gnupg2 make vim wget && \
    rm -rf /var/lib/apt/lists
