import json
import os
import torch

import numpy as np
from scipy.io import wavfile


def fix_segment_start_end_timings(transcript_fixed_json, vocals_wav, convolution_window=0.05, threshold=50, force=False):
    output_file = f'{os.path.dirname(transcript_fixed_json)}/transcript-fixed-2.json'
    if os.path.exists(output_file) and not force:
        return output_file

    voice_segments_dir = f'{os.path.dirname(transcript_fixed_json)}/voice-segments'
    if not os.path.exists(voice_segments_dir):
        os.makedirs(voice_segments_dir)

    # read audio rate and data
    rate, original_data = wavfile.read(vocals_wav)
    data = original_data
    nb_channels = len(data[0])
    print(f"number of channels = {nb_channels}")
    length = data.shape[0] / rate
    print(f"audio duration = {length} seconds")

    data = np.absolute(data)
    print("end of absolute")

    # average stereo channels
    if nb_channels == 2:
        data = np.matmul(data, np.array([0.5, 0.5]))
    print("end merge channels")


    # convolution
    conv_shape = round(rate * convolution_window)
    conv = np.full((conv_shape), 1/conv_shape)
    data = np.convolve(data, conv, 'same')
    print("end of convolution")

    # max value and voice detection threshold
    max_value = np.max(data)
    threshold = max_value / threshold
    data = np.array([0 if a_ < threshold else 1 for a_ in data])


    min_silence_duration = round(rate*0.2)
    min_voice_duration = round(rate*0.2)


    # pooling = torch.nn.MaxPool1d(min_silence_duration, stride=1)
    # data_tensor = torch.from_numpy(data).float()
    # output_tensor = pooling(data_tensor[None, ...])
    # data = output_tensor.detach().cpu().numpy()[0]

    # import matplotlib.pyplot as plt
    # time = np.linspace(0., length, data.shape[0])
    # plt.plot(time, data, label="Audio")
    # plt.legend()
    # plt.xlabel("Time [s]")
    # plt.ylabel("Merged")
    # plt.show()
    # return

    in_silence = True
    voice_start_segment_index = None
    voice_end_segment_index = None
    silence_start_segment_index = 0
    silence_end_segment_index = None
    segment_index = 0
    for i in range(0, len(data)):
        if in_silence:
            if data[i] != 0:
                # go in voice state
                in_silence = False
                # maybe we are back from a short silence so don't overwrite previous voice start
                if voice_start_segment_index is None:
                    # set start/end of voice markers
                    voice_start_segment_index = i
                    voice_end_segment_index = i
                # reset start/end of silence markers
                silence_start_segment_index = None
                silence_end_segment_index = None
            else:
                # still in silence
                # move the end of silence marker
                silence_end_segment_index = i
                # if silence is large enough and if a voice segment has been found, write it
                if (voice_end_segment_index is not None and
                        silence_end_segment_index - silence_start_segment_index > min_silence_duration  and
                        voice_end_segment_index - voice_start_segment_index > min_voice_duration):
                    wavfile.write(f'{voice_segments_dir}/segment-{"{:04d}".format(segment_index)}.wav', rate,
                                  original_data[voice_start_segment_index:voice_end_segment_index])
                    voice_start_segment_index = None
                    voice_end_segment_index = None
                    segment_index += 1
        else:
            if data[i] != 0:
                # still in voice
                # move the end of voice marker
                voice_end_segment_index = i
            else:
                # back to silence state
                in_silence = True
                # set start/end of silence markers
                silence_start_segment_index = i
                silence_end_segment_index = i
    if voice_end_segment_index is not None:
        wavfile.write(f'{voice_segments_dir}/segment-{"{:03d}".format(segment_index)}.wav', rate,
                      original_data[voice_start_segment_index:voice_end_segment_index])

    # # max value and voice detection threshold
    # max_value = np.max(data4)
    # threshold = max_value / threshold
    # data5 = [0 if a_ < threshold else 1 for a_ in data4]

    # plotting the audio time and amplitude
    import matplotlib.pyplot as plt
    time = np.linspace(0., length, data.shape[0])
    plt.plot(time, data, label="Audio")
    plt.legend()
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.show()

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
    # project_dir = get_sample_project_dir('dancing_in_the_dark')
    project_dir = get_sample_project_dir('ma_direction')
    threshold = 50
    convolution_window = 0.05
    fix_segment_start_end_timings(f'{project_dir}/transcript-fixed.json', f'{project_dir}/vocals.wav',
                                  convolution_window=convolution_window, threshold=threshold, force=True)
