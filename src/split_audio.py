# adapted from:
# https://dsp.stackexchange.com/questions/17628/python-audio-detecting-silence-in-audio-signal
# https://gist.githubusercontent.com/rudolfbyker/8fc0d99ecadad0204813d97fee2c6c06/raw/bb728ca20cb6bb6b6c4d1091f11f5c1e385840ec/split_wav.py
import json
import sys
from pathlib import Path

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
def split_audio(input_filename, target_filename=None, base_output_dir=None, silence_threshold=1e-6, min_silence_length=3., step_duration=None, remove_silences=False, split_file=False, force=False):
    window_duration = min_silence_length
    if step_duration is None:
        step_duration = window_duration / 10.
    params = {
        'input_filename': os.path.basename(input_filename),
        'target_filename': os.path.basename(input_filename) if target_filename is None else os.path.basename(target_filename),
        'silence_threshold': silence_threshold,
        'min_silence_length': min_silence_length,
        'step_duration': step_duration,
    }
    summary_json = f'{os.path.dirname(input_filename)}/split-summary.json'
    no_silence_filename = f'{Path(os.path.basename(input_filename)).stem}-no-silence.wav'
    no_silence_waw = f"{os.path.dirname(input_filename)}/{no_silence_filename}"
    if remove_silences and os.path.exists(summary_json) and os.path.exists(no_silence_waw) and not force:
        return summary_json, no_silence_waw

    if base_output_dir is None:
        base_output_dir = os.path.dirname(input_filename)
    if not recompute_required(summary_json, base_output_dir, params, force):
        return summary_json

    output_dir = f'{base_output_dir}/voice-segments'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    segments = []
    silence_cuts = []
    summary = {
        'params': params,
        'segments': segments,
        'total' : None,
        'silence_cuts': silence_cuts
    }
    output_filename_prefix = os.path.splitext(os.path.basename(input_filename if target_filename is None else target_filename))[0]
    print("Splitting {} where energy is below {}% for longer than {}s.".format(
        input_filename,
        silence_threshold * 100.,
        window_duration
    ))

    # Read and split the file

    sample_rate, samples = wavfile.read(filename=input_filename)
    target_samples = samples
    if target_filename is not None:
        target_sample_rate, target_samples = wavfile.read(filename=target_filename)
        assert target_sample_rate == sample_rate
        assert len(target_samples) == len(samples)

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
    samples_no_silences = []
    max_silence_in_seconds = 1
    nb_max_silence_samples = int(max_silence_in_seconds * sample_rate)
    last_end_point = 0
    nb_cumulated_removed_silence_samples = 0
    for i, start, stop in tqdm(cut_ranges):
        segments.append(trim_right_silence_and_write_file(split_file, i, max_energy, output_dir, output_filename_prefix, sample_rate,
                                                          samples, target_samples, silence_threshold, start, step_size, stop, window_size))
        if remove_silences:
            start_point = segments[-1]['start_point']
            end_point = segments[-1]['end_point']
            # acutal silence duration
            nb_silence_samples = start_point - last_end_point
            nb_removed_silence_samples = 0
            # coerce to max duration
            if nb_silence_samples > nb_max_silence_samples:
                nb_removed_silence_samples = nb_silence_samples - nb_max_silence_samples
                nb_cumulated_removed_silence_samples += nb_removed_silence_samples
                nb_silence_samples = nb_max_silence_samples
                # remember the cut
                silence_cut = {
                    # mark the cut in the middle to prevent alignment error when shifting back
                    "at_point": len(samples_no_silences) + int(nb_max_silence_samples / 2),
                    "at_original_point": last_end_point + int(nb_max_silence_samples / 2),
                    "removed_points": nb_removed_silence_samples,
                    "cumulated_removed_points": nb_cumulated_removed_silence_samples,
                }
                silence_cut['at'] = silence_cut[f'at_point'] / sample_rate
                silence_cut['at_original'] = silence_cut[f'at_original_point'] / sample_rate
                silence_cut['removed'] = silence_cut[f'removed_points'] / sample_rate
                silence_cut['cumulated_removed'] = silence_cut[f'cumulated_removed_points'] / sample_rate
                silence_cuts.append(silence_cut)
            # insert silence in the audio
            for i in range(0, nb_silence_samples):
                samples_no_silences.append([0, 0])
            # add non-silence
            for i in range(start_point, end_point):
                samples_no_silences.append([samples[i][0], samples[i][1]])
            last_end_point = end_point

    no_silence_filename = None
    if remove_silences:
        np_samples_no_silences = np.array(samples_no_silences, dtype=int).astype(np.int16)
        wavfile.write(
            filename=no_silence_waw,
            rate=sample_rate,
            data=np_samples_no_silences
        )

    summary["total"] = {
        'start_point': 0,
        'end_point': len(samples),
        'start': (0 / sample_rate),
        'end': (len(samples) / sample_rate),
        'file': input_filename
    }
    with open(summary_json, mode="w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)
    return summary_json, no_silence_waw


def recompute_required(summary_json, base_output_dir, params, force):
    output_dir = f'{base_output_dir}/voice-segments'
    all_wav_files = {file for file in os.listdir(output_dir) if file.endswith('.wav')} if os.path.exists(output_dir) else set()
    removed_wav_files = all_wav_files
    if not os.path.exists(summary_json):
        force = True
    else:
        with open(summary_json, mode='r', encoding='utf-8') as file:
            summary = json.load(file)
        # not the same params => must recompute voice segments
        referenced_wav_files = set()
        if summary['params'] != params:
            force = True
        else:
            for segment in summary['segments']:
                file = segment['file']
                if os.path.exists(f'{base_output_dir}/{file}'):
                    referenced_wav_files.add(os.path.basename(file))
                else:
                    # one file missing => must recompute voice segments
                    force = True
        removed_wav_files = all_wav_files if force else all_wav_files.difference(referenced_wav_files)
    for wav_file in removed_wav_files:
        os.remove(f'{output_dir}/{wav_file}')
    return force


def trim_right_silence_and_write_file(split_file, i, max_energy, output_dir, output_filename_prefix, sample_rate, samples, target_samples,
                                      silence_threshold, start, step_size, stop, window_size):
    sub_signal_rev_windows = rev_windows(
        signal=samples[start:stop],
        window_size=window_size,
        step_size=step_size
    )
    if stop == -1:
        stop = len(samples)
    truncate_right = 0
    for sub_signal_window in sub_signal_rev_windows:
        if energy(sub_signal_window) / max_energy > silence_threshold:
            break
        else:
            truncate_right += step_size
    stop -= truncate_right
    output_filename = "{}_{:03d}.wav".format(
        output_filename_prefix,
        i
    )
    rel_output_dir = os.path.basename(output_dir)
    output_file_path = os.path.join(output_dir, output_filename)
    if not split_file:
        print("Writing file {}".format(output_file_path))
        wavfile.write(
            filename=output_file_path,
            rate=sample_rate,
            data=target_samples[start:stop]
        )
    return {
        'start_point': start,
        'end_point': stop,
        'start': (start / sample_rate),
        'end': (stop / sample_rate),
        'file': f'{rel_output_dir}/{output_filename}',
    }


if __name__ == '__main__':
    if False and len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='Split a WAV file at silence.')
        parser.add_argument('input_file', type=str, help='The WAV file to split.')
        parser.add_argument('--output-dir', '-o', type=str, default=None,
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
        split_audio(input_filename, None, output_dir, silence_threshold, min_silence_length, step_duration, dry_run)
    else:
        from projects import get_project_dir
        project_name = 'slash-far-and-away'
        project_dir = get_project_dir(project_name)
        split_audio(f'{project_dir}/vocals.wav', f'{project_dir}/audio.wav', silence_threshold=0.001, remove_silences=True, min_silence_length=0.5, split_file=True, force=True)


