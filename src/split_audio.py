# adapted from:
# https://dsp.stackexchange.com/questions/17628/python-audio-detecting-silence-in-audio-signal
# https://gist.githubusercontent.com/rudolfbyker/8fc0d99ecadad0204813d97fee2c6c06/raw/bb728ca20cb6bb6b6c4d1091f11f5c1e385840ec/split_wav.py

# un peu trop coupé
# --silence-threshold 0.001 --min-silence-length 0.4 --output-dir ../output/sexion-dassaut-ma-direction-clip-officiel/voice-segments ../output/sexion-dassaut-ma-direction-clip-officiel/vocals.wav
# plus homognène
# --silence-threshold 0.001 --min-silence-length 0.45 --output-dir ../output/sexion-dassaut-ma-direction-clip-officiel/voice-segments ../output/sexion-dassaut-ma-direction-clip-officiel/vocals.wav
# trop coupé
# --silence-threshold 0.0025 --min-silence-length 0.45 --output-dir ../output/sexion-dassaut-ma-direction-clip-officiel/voice-segments ../output/sexion-dassaut-ma-direction-clip-officiel/vocals.wav
# encore trop coupé
# --silence-threshold 0.0015 --min-silence-length 0.45 --output-dir ../output/sexion-dassaut-ma-direction-clip-officiel/voice-segments ../output/sexion-dassaut-ma-direction-clip-officiel/vocals.wav
# encore trop coupé
# --silence-threshold 0.00125 --min-silence-length 0.45 --output-dir ../output/sexion-dassaut-ma-direction-clip-officiel/voice-segments ../output/sexion-dassaut-ma-direction-clip-officiel/vocals.wav


# trop coupé
# --silence-threshold 0.0011 --min-silence-length 0.2 --output-dir ../output/sexion-dassaut-ma-direction-clip-officiel/voice-segments/vocals_31 ../output/sexion-dassaut-ma-direction-clip-officiel/voice-segments/vocals_031.wav

from scipy.io import wavfile
import os
import numpy as np
import argparse
from tqdm import tqdm

# Utility functions

def windows(signal, window_size, step_size):
    if type(window_size) is not int:
        raise AttributeError("Window size must be an integer.")
    if type(step_size) is not int:
        raise AttributeError("Step size must be an integer.")
    for i_start in range(0, len(signal), step_size):
        i_end = i_start + window_size
        if i_end >= len(signal):
            break
        yield signal[i_start:i_end]

def rev_windows(signal, window_size, step_size):
    if type(window_size) is not int:
        raise AttributeError("Window size must be an integer.")
    if type(step_size) is not int:
        raise AttributeError("Step size must be an integer.")
    for i_start in range(0, len(signal), step_size):
        i_end = i_start + window_size
        if i_end >= len(signal):
            break
        yield signal[len(signal)-i_end:len(signal)-i_start]

def energy(samples):
    return np.sum(np.power(samples, 2.)) / float(len(samples))

def rising_edges(binary_signal):
    previous_value = 0
    index = 0
    for x in binary_signal:
        if x and not previous_value:
            yield index
        previous_value = x
        index += 1

# main function
def split_audio(input_filename, output_dir, silence_threshold=1e-6, min_silence_length=3., step_duration=None, dry_run=False):
    output_filename_prefix = os.path.splitext(os.path.basename(input_filename))[0]
    window_duration = min_silence_length
    if step_duration is None:
        step_duration = window_duration / 10.
    print("Splitting {} where energy is below {}% for longer than {}s.".format(
        input_filename,
        silence_threshold * 100.,
        window_duration
    ))

    # Read and split the file

    sample_rate, samples =wavfile.read(filename=input_filename)

    max_amplitude = np.iinfo(samples.dtype).max
    max_energy = energy([max_amplitude])
    window_size = int(window_duration * sample_rate)
    step_size = int(step_duration * sample_rate)
    signal_windows = windows(
        signal=samples,
        window_size=window_size,
        step_size=step_size
    )
    window_energy = (energy(w) / max_energy for w in tqdm(
        signal_windows,
        total=int(len(samples) / float(step_size))
    ))
    window_silence = (e > silence_threshold for e in window_energy)
    cut_times = (r * step_duration for r in rising_edges(window_silence))
    # This is the step that takes long, since we force the generators to run.
    print("Finding silences...")
    cut_samples = [int(t * sample_rate) for t in cut_times]
    cut_samples.append(-1)
    cut_ranges = [(i, cut_samples[i], cut_samples[i + 1]) for i in range(len(cut_samples) - 1)]
    segments = []
    last_stop = None
    last_i = None
    for i, start, stop in tqdm(cut_ranges):
        last_stop = stop
        last_i = i
        trim_right_silence_and_write_file(dry_run, i, max_energy, output_dir, output_filename_prefix, sample_rate,
                                          samples, silence_threshold, start, step_size, stop, window_size)
    if last_stop is not None and last_stop < len(samples):
        trim_right_silence_and_write_file(dry_run, last_i+1, max_energy, output_dir, output_filename_prefix, sample_rate,
                                          samples, silence_threshold, last_stop, step_size, len(samples), window_size)
    return segments


def trim_right_silence_and_write_file(dry_run, i, max_energy, output_dir, output_filename_prefix, sample_rate, samples,
                                      silence_threshold, start, step_size, stop, window_size):
    sub_signal_rev_windows = rev_windows(
        signal=samples[start:stop],
        window_size=window_size,
        step_size=step_size
    )
    truncate_right = 0
    for sub_signal_window in sub_signal_rev_windows:
        if energy(sub_signal_window) / max_energy > silence_threshold:
            break
        else:
            truncate_right += step_size
    stop -= truncate_right
    output_file_path = "{}_{:03d}.wav".format(
        os.path.join(output_dir, output_filename_prefix),
        i
    )
    if not dry_run:
        print("Writing file {}".format(output_file_path))
        wavfile.write(
            filename=output_file_path,
            rate=sample_rate,
            data=samples[start:stop]
        )
    else:
        print("Not writing file {}".format(output_file_path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Split a WAV file at silence.')
    parser.add_argument('input_file', type=str, help='The WAV file to split.')
    parser.add_argument('--output-dir', '-o', type=str, default='.',
                        help='The output folder. Defaults to the current folder.')
    parser.add_argument('--min-silence-length', '-m', type=float, default=3.,
                        help='The minimum length of silence at which a split may occur [seconds]. Defaults to 3 seconds.')
    parser.add_argument('--silence-threshold', '-t', type=float, default=1e-6,
                        help='The energy level (between 0.0 and 1.0) below which the signal is regarded as silent. Defaults to 1e-6 == 0.0001%.')
    parser.add_argument('--step-duration', '-s', type=float, default=None,
                        help='The amount of time to step forward in the input file after calculating energy. Smaller value = slower, but more accurate silence detection. Larger value = faster, but might miss some split opportunities. Defaults to (min-silence-length / 10.).')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Don\'t actually write any output files.')

    # Process command line arguments
    args = parser.parse_args()
    input_filename = args.input_file
    min_silence_length = args.min_silence_length
    if args.step_duration is None:
        step_duration = min_silence_length / 10.
    else:
        step_duration = args.step_duration
    silence_threshold = args.silence_threshold
    output_dir = args.output_dir
    dry_run = args.dry_run
    split_audio(input_filename, output_dir, silence_threshold, min_silence_length, step_duration, dry_run)
