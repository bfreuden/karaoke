import json
import os

import numpy as np
from scipy.io import wavfile


def fix_segment_start_end_timings(transcript_fixed_json, vocals_wav, convolution_window=0.05, threshold=50, force=False):
    output_file = f'{os.path.dirname(transcript_fixed_json)}/transcript-fixed-2.json'
    if os.path.exists(output_file) and not force:
        return output_file
    # read audio rate and data
    rate, data = wavfile.read(vocals_wav)
    nb_channels = len(data[0])
    print(f"number of channels = {nb_channels}")
    length = data.shape[0] / rate
    print(f"audio duration = {length} seconds")
    # average stereo channels
    if nb_channels == 2:
        data2 = np.matmul(data, np.array([0.5, 0.5]))
    else:
        data2 = data
    # convolution on 0.05 seconds window
    conv_shape = round(rate * convolution_window)
    conv = np.full((conv_shape), 1/conv_shape)

    # max value and voice detection threshold
    max_value = np.max(data2)
    threshold = max_value / threshold
    data3 = [0 if a_ < threshold else 1 for a_ in data2]

    data4 = np.convolve(data3, conv, 'same')

    # max value and voice detection threshold
    max_value = np.max(data4)
    threshold = max_value / threshold
    data5 = [0 if a_ < threshold else 1 for a_ in data4]

    # plotting the audio time and amplitude
    # import matplotlib.pyplot as plt
    # time = np.linspace(0., length, data.shape[0])
    # plt.plot(time, data5, label="Audio")
    # plt.legend()
    # plt.xlabel("Time [s]")
    # plt.ylabel("Amplitude")
    # plt.show()

    with open(transcript_fixed_json, mode='r', encoding="utf-8") as file:
        transcript_fixed = json.load(file)

    last_end_pos_in_wav = 0

    for idx, segment in enumerate(transcript_fixed['segments']):
        # adjust start of segment
        start = segment['words'][0]['start']
        end_first_word = segment['words'][0]['end']
        start_pos_in_wav = round(start * rate)
        end_first_word_in_wav = round(end_first_word * rate)
        if data4[start_pos_in_wav] == 0:
            # => in a silence zone
            # we need to move forward
            incr = 1
            # until we find voice
            target_value = 1
            # but not beyond
            limit = end_first_word_in_wav
        else:
            # => in a voice zone
            # we need to move backward
            incr = -1
            # until we find silence
            target_value = 0
            # but not beyond
            limit = last_end_pos_in_wav
        while data4[start_pos_in_wav] != target_value and start_pos_in_wav != limit:
            start_pos_in_wav += incr
        new_start = start_pos_in_wav / rate
        segment['words'][0]['start'] = new_start

        # adjust end of segment
        end = segment['words'][-1]['end']
        start_last_word = segment['words'][-1]['start']
        start_last_word_in_wav = round(start_last_word * rate)
        end_pos_in_wav = round(end * rate)
        if data4[end_pos_in_wav] == 0:
            # => in a silence zone
            # we need to move backward
            incr = -1
            # until we find voice
            target_value = 1
            # but not beyond
            limit = start_last_word_in_wav
        else:
            # we need to move forward
            incr = 1
            # until we find silence
            target_value = 0
            # but not after
            limit = 0
        while data4[end_pos_in_wav] != target_value and (limit == 0 or end_pos_in_wav != limit):
            end_pos_in_wav += incr
        new_end = end_pos_in_wav / rate
        segment['words'][-1]['end'] = new_end

        print(f'segment {idx}:')
        print(f' start: {start}')
        print(f'    =>: {new_start}')
        print(f'   end: {end}')
        print(f'    =>: {new_end}')

    with open(output_file, mode='w', encoding="utf-8") as file:
        json.dump(transcript_fixed, file, indent=2, ensure_ascii=False)

    return output_file

if __name__ == '__main__':

    from sample_projects import get_sample_project_dir
    project_dir = get_sample_project_dir('dancing_in_the_dark')
    threshold = 50
    convolution_window = 0.05
    fix_segment_start_end_timings(f'{project_dir}/transcript-fixed.json', f'{project_dir}/vocals.wav',
                                  convolution_window=convolution_window, threshold=threshold, force=True)
