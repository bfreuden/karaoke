#!/bin/bash

docker run --rm --mount type=bind,src=$(pwd)/input,dst=/input --mount type=bind,src=$(pwd)/output,dst=/output bfreudens/nemo-forced-aligner:2.2.1 python3 align.py manifest_filepath=/input/manifest.json pretrained_name="stt_en_fastconformer_hybrid_large_pc"  output_dir=/output

