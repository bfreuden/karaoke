FROM ubuntu:22.04

RUN apt update && \
    apt install -y \
      curl \
      unzip \
      python3.10 \
      python3-pip \
      libsndfile1 \
      ffmpeg \
      sox && \
    apt-get clean all -y

WORKDIR /opt

RUN curl -o v2.2.1.zip https://codeload.github.com/NVIDIA/NeMo/zip/refs/tags/v2.2.1 && \
    unzip v2.2.1.zip && \
    rm v2.2.1.zip


WORKDIR /opt/NeMo-2.2.1

RUN pip3 --no-cache-dir install "numpy<2.0.0"
RUN pip3 --no-cache-dir install typing-extensions
RUN pip3 --no-cache-dir install sox
RUN pip3 --no-cache-dir install '.[asr]'

RUN echo '{"audio_filepath": "/usr/local/lib/python3.10/dist-packages/IPython/lib/tests/test.wav", "text": "test"}' > /tmp/manifest.json

WORKDIR /opt/NeMo-2.2.1/tools/nemo_forced_aligner

RUN python3 align.py manifest_filepath=/tmp/manifest.json pretrained_name="stt_en_fastconformer_hybrid_large_pc"  output_dir=/tmp
RUN python3 align.py manifest_filepath=/tmp/manifest.json pretrained_name="nvidia/stt_fr_fastconformer_hybrid_large_pc"  output_dir=/tmp

RUN mkdir /input && \
    mkdir /output && \
    mkdir /exchange && \
    chmod ugo+rwx /input && \
    chmod ugo+rwx /output && \
    chmod ugo+rwx /exchange

COPY ./docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
