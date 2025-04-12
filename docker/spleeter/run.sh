#!/bin/bash

docker run --rm --mount type=bind,src=$(pwd)/input,dst=/input --mount type=bind,src=$(pwd)/output,dst=/output bfreudens/spleeter:2.4.2 python3 spleet.py /input/audio.mp3

