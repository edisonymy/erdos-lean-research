FROM ubuntu:24.04@sha256:4fbb8e6a8395de5a7550b33509421a2bafbc0aab6c06ba2cef9ebffbc7092d90

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       build-essential ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/arminbiere/cadical.git /opt/cadical \
    && git -C /opt/cadical checkout 146207318796f094dcded87349a64f0c6927309e

RUN git clone https://github.com/marijnheule/drat-trim.git /opt/drat-trim \
    && git -C /opt/drat-trim checkout 2e3b2dc0ecf938addbd779d42877b6ed69d9a985 \
    && make -C /opt/drat-trim

WORKDIR /opt/cadical
RUN ./configure && make -j2

ENTRYPOINT ["/opt/cadical/build/cadical"]
