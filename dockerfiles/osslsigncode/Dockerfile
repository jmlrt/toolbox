FROM debian:stable-20210111-slim as builder
RUN apt-get update && apt-get install -y build-essential autoconf libtool libssl-dev python3-pkgconfig libcurl4-gnutls-dev wget
RUN wget https://github.com/mtrojnar/osslsigncode/archive/2.0.tar.gz && \
    tar xzf 2.0.tar.gz && \
    cd osslsigncode-2.0 && \
    ./autogen.sh && \
    ./configure && \
    make

FROM debian:stable-20210111-slim
RUN apt-get update && apt-get install -y libssl-dev libcurl4-gnutls-dev
WORKDIR /data/
COPY --from=builder ./osslsigncode-2.0/osslsigncode /usr/local/bin/osslsigncode
