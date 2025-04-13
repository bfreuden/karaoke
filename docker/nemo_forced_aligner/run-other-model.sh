#!/bin/bash

docker run --rm -v nemo-nfa-models:/root/.cache/torch/NeMo --mount type=bind,src=$(pwd)/input,dst=/input --mount type=bind,src=$(pwd)/output,dst=/output bfreudens/nemo-forced-aligner:2.2.1 python3 align.py manifest_filepath=/input/manifest.json additional_segment_grouping_separator="|" pretrained_name="nvidia/stt_en_fastconformer_transducer_large"  output_dir=/output

