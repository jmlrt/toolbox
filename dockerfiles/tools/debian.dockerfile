FROM debian:10

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y gnupg2 make vim && \
    apt-get clean
