FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    git cmake g++ make libboost-all-dev zlib1g-dev libgmp-dev \
    && rm -rf /var/lib/apt/lists/*

# These are the exact commits used by results.json.  The Glasgow commit is the
# submodule recorded by the pinned SMS commit; it is stated explicitly here.
RUN git clone --recursive https://github.com/markirch/sat-modulo-symmetries /opt/sms \
    && cd /opt/sms \
    && git checkout 464f12f1fd36b496e7ba9dcbb622b079de02dce4 \
    && git submodule update --init --recursive \
    && cd glasgow-subgraph-solver \
    && git checkout 1217f5b82ce62c2c2f227002eedb029765da74f3 \
    && cd ../cadical_sms \
    && git checkout b023aaf059babf867a7fdfc5fb342d52ffbccb25 \
    && cd .. \
    && sed -i '/libglasgow_subgraphs.a/a link_libraries(gmpxx gmp)' CMakeLists.txt \
    && bash build-and-install.sh -s -l \
    && pip install --no-cache-dir . networkx

ENV LD_LIBRARY_PATH=/root/.local/lib:/usr/local/lib
ENV PATH=/root/.local/bin:/usr/local/bin:/usr/bin:/bin
WORKDIR /work
