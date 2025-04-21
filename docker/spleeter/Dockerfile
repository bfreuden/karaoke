FROM ubuntu:22.04

RUN apt update && \
    apt install -y \
      curl \
      unzip \
      python3.10 \
      python3-pip \
      ffmpeg && \
    apt-get clean all -y

RUN mkdir -p /opt/spleeter/pretrained_models/2stems

WORKDIR /opt/spleeter/pretrained_models/2stems

RUN curl -L -o 2stems.tar.gz 'https://github.com/deezer/spleeter/releases/download/v1.4.0/2stems.tar.gz' && \
    gunzip 2stems.tar.gz && \
    tar xvf 2stems.tar && \
    rm 2stems.tar

WORKDIR /opt/spleeter

RUN pip3 --no-cache-dir install spleeter==2.4.2
RUN pip3 --no-cache-dir install argparse

RUN mkdir /input && \
    mkdir /output && \
    mkdir /exchange && \
    chmod ugo+rwx /input && \
    chmod ugo+rwx /output && \
    chmod ugo+rwx /exchange

COPY ./docker-entrypoint.sh /usr/local/bin/
COPY ./spleet.py /opt/spleeter/

ENV MODEL_PATH=/opt/spleeter/pretrained_models

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
