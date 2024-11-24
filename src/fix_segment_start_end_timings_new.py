import json
import os
import torch
import numpy as np
from scipy.io import wavfile

def fix_segment_start_end_timings(transcript_fixed_json, vocals_wav, convolution_window=0.05, silence_threshold=50, force=False):

    output_file = f'{os.path.dirname(transcript_fixed_json)}/transcript-fixed-2.json'
    if os.path.exists(output_file) and not force:
        return output_file

    voice_segments_dir = f'{os.path.dirname(transcript_fixed_json)}/voice-segments'
    if force and os.path.exists(voice_segments_dir):
        for file in os.listdir(voice_segments_dir):
            os.remove(f'{voice_segments_dir}/{file}')
    if not os.path.exists(voice_segments_dir):
        os.makedirs(voice_segments_dir)

    # read audio rate and data
    rate, original_data = wavfile.read(vocals_wav)
    data = original_data
    nb_channels = len(data[0])
    audio_duration_in_sec = data.shape[0] / rate
    print(f"number of channels = {nb_channels}")
    print(f"audio duration = {audio_duration_in_sec} seconds")

    data = merge_stereo_channels(data, audio_duration_in_sec, nb_channels, plot=True)

    # data = apply_boost_highs(data, audio_duration_in_sec, 0.8, plot=True)
    data = apply_flatten_lows(data, audio_duration_in_sec, 0.2, plot=True)

    #
    # data = to_steps(data, audio_duration_in_sec, silence_threshold, plot=True)

    # gaussian_filter_radius_in_seconds = 0.1
    # data = apply_gaussian_filtering(data, gaussian_filter_radius_in_seconds, audio_duration_in_sec, rate, plot=True)
    #
    # data = apply_derivative(data, 100, audio_duration_in_sec, plot=True)


    pooling_radius_in_seconds = 0.1
    data = apply_max_pooling(data, pooling_radius_in_seconds, audio_duration_in_sec, rate, plot=True)
    # data = to_steps(data, audio_duration_in_sec, 2, plot=True)

    return True
    in_silence = True
    voice_start_segment_index = None
    voice_end_segment_index = None
    silence_start_segment_index = 0
    silence_end_segment_index = None
    segment_index = 0
    min_silence_duration = round(rate*0.2)
    min_voice_duration = round(rate*0.2)
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
        wavfile.write(f'{voice_segments_dir}/segment-{"{:04d}".format(segment_index)}.wav', rate,
                      original_data[voice_start_segment_index:voice_end_segment_index])

    # # max value and voice detection silence_threshold
    # max_value = np.max(data4)
    # silence_threshold = max_value / silence_threshold
    # data5 = [0 if a_ < silence_threshold else 1 for a_ in data4]


    # with open(transcript_fixed_json, mode='r', encoding="utf-8") as file:
    #     transcript_fixed = json.load(file)
    #
    # last_end_pos_in_wav = 0
    #
    # for idx, segment in enumerate(transcript_fixed['segments']):
    #     # adjust start of segment
    #     start = segment['words'][0]['start']
    #     end_first_word = segment['words'][0]['end']
    #     start_pos_in_wav = round(start * rate)
    #     end_first_word_in_wav = round(end_first_word * rate)
    #     if data4[start_pos_in_wav] == 0:
    #         # => in a silence zone
    #         # we need to move forward
    #         incr = 1
    #         # until we find voice
    #         target_value = 1
    #         # but not beyond
    #         limit = end_first_word_in_wav
    #     else:
    #         # => in a voice zone
    #         # we need to move backward
    #         incr = -1
    #         # until we find silence
    #         target_value = 0
    #         # but not beyond
    #         limit = last_end_pos_in_wav
    #     while data4[start_pos_in_wav] != target_value and start_pos_in_wav != limit:
    #         start_pos_in_wav += incr
    #     new_start = start_pos_in_wav / rate
    #     segment['words'][0]['start'] = new_start
    #
    #     # adjust end of segment
    #     end = segment['words'][-1]['end']
    #     start_last_word = segment['words'][-1]['start']
    #     start_last_word_in_wav = round(start_last_word * rate)
    #     end_pos_in_wav = round(end * rate)
    #     if data4[end_pos_in_wav] == 0:
    #         # => in a silence zone
    #         # we need to move backward
    #         incr = -1
    #         # until we find voice
    #         target_value = 1
    #         # but not beyond
    #         limit = start_last_word_in_wav
    #     else:
    #         # we need to move forward
    #         incr = 1
    #         # until we find silence
    #         target_value = 0
    #         # but not after
    #         limit = 0
    #     while data4[end_pos_in_wav] != target_value and (limit == 0 or end_pos_in_wav != limit):
    #         end_pos_in_wav += incr
    #     new_end = end_pos_in_wav / rate
    #     segment['words'][-1]['end'] = new_end
    #
    #     print(f'segment {idx}:')
    #     print(f' start: {start}')
    #     print(f'    =>: {new_start}')
    #     print(f'   end: {end}')
    #     print(f'    =>: {new_end}')
    #
    # with open(output_file, mode='w', encoding="utf-8") as file:
    #     json.dump(transcript_fixed, file, indent=2, ensure_ascii=False)
    #
    # return output_file


def to_steps(data, data_duration_in_seconds, silence_threshold, plot=False):
    # max value and voice detection silence_threshold
    max_value = np.max(data)
    silence_value = max_value / silence_threshold
    data = np.array([0 if x < silence_value else 1 for x in data])
    if plot:
        import matplotlib.pyplot as plt
        time = np.linspace(0., data_duration_in_seconds, data.shape[0])
        plt.plot(time, data, label="Audio")
        plt.legend()
        plt.xlabel("Time [s]")
        plt.ylabel("Steps")
        plt.show()
    return data

def apply_boost_highs(data, data_duration_in_seconds, high_threshold_percent, plot=False):
    max_value = np.max(data)
    high_threshold = max_value * high_threshold_percent
    data = np.array([max_value if x > high_threshold else x for x in data])
    if plot:
        import matplotlib.pyplot as plt
        time = np.linspace(0., data_duration_in_seconds, data.shape[0])
        plt.plot(time, data, label="Audio")
        plt.legend()
        plt.xlabel("Time [s]")
        plt.ylabel("Boost highs")
        plt.show()
    return data

def apply_flatten_lows(data, data_duration_in_seconds, low_threshold_percent, plot=False):
    max_value = np.max(data)
    low_threshold = max_value * low_threshold_percent
    data = np.array([0 if x < low_threshold else x for x in data])
    if plot:
        import matplotlib.pyplot as plt
        time = np.linspace(0., data_duration_in_seconds, data.shape[0])
        plt.plot(time, data, label="Audio")
        plt.legend()
        plt.xlabel("Time [s]")
        plt.ylabel("Flatten lows")
        plt.show()
    return data


def merge_stereo_channels(data, data_duration_in_seconds, nb_channels, plot=False):
    # remove sign
    data = np.absolute(data)
    # average stereo channels
    if nb_channels == 2:
        data = np.matmul(data, np.array([0.5, 0.5]))
    if plot:
        import matplotlib.pyplot as plt
        time = np.linspace(0., data_duration_in_seconds, data.shape[0])
        plt.plot(time, data, label="Audio")
        plt.legend()
        plt.xlabel("Time [s]")
        plt.ylabel("Merged")
        plt.show()
    return data


def apply_max_pooling(data, pooling_radius_in_seconds, audio_duration_in_seconds, rate, plot=False):
    pooling = torch.nn.MaxPool1d(round(rate * 2 * pooling_radius_in_seconds), stride=1)
    data_tensor = torch.from_numpy(data).float()
    output_tensor = pooling(data_tensor[None, ...])
    data = output_tensor.detach().cpu().numpy()[0]
    if plot:
        import matplotlib.pyplot as plt
        time = np.linspace(0., audio_duration_in_seconds, data.shape[0])
        plt.plot(time, data, label="Audio")
        plt.legend()
        plt.xlabel("Time [s]")
        plt.ylabel("Max pooling")
        plt.show()
    print("end of pooling")
    return data


def apply_gaussian_filtering(data, filter_radius_in_seconds, audio_duration_in_seconds, rate, plot=False):

    # convolution
    # conv_shape = round(rate * convolution_window)
    # conv = np.full((conv_shape), 1/conv_shape)

    x_s = np.linspace(-0.5, 0.5, round(rate * 2 * filter_radius_in_seconds))
    mu, sigma = 0, 0.1
    gaussian = np.array([1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(- (x - mu) ** 2 / (2 * sigma ** 2)) for x in x_s])
    if plot:
        import matplotlib.pyplot as plt
        plt.plot(x_s, gaussian, linewidth = 2, color = 'r')
        plt.ylabel("Gaussian")
        plt.show()
    data = np.convolve(data, gaussian, 'same')
    print("end of gaussian filtering")

    if plot:
        import matplotlib.pyplot as plt
        time = np.linspace(0., audio_duration_in_seconds, data.shape[0])
        plt.plot(time, data, label="Audio")
        plt.legend()
        plt.xlabel("Time [s]")
        plt.ylabel("Gaussian filter")
        plt.show()
    return data


def apply_derivative(data, multiplier, audio_duration_in_seconds, plot=False):

    derivative = np.array([*([-1.0]*multiplier), 0, *([1.0]*multiplier)])
    data = np.convolve(data, derivative, 'same')
    print("end of derivative")

    if plot:
        import matplotlib.pyplot as plt
        time = np.linspace(0., audio_duration_in_seconds, data.shape[0])
        plt.plot(time, data, label="Audio")
        plt.legend()
        plt.xlabel("Time [s]")
        plt.ylabel("Derivative")
        plt.show()
    return data


if __name__ == '__main__':

    from sample_projects import get_sample_project_dir
    # project_dir = get_sample_project_dir('dancing_in_the_dark')
    project_dir = get_sample_project_dir('ma_direction')
    silence_threshold = 40
    convolution_window = 0.05
    fix_segment_start_end_timings(f'{project_dir}/transcript-fixed.json', f'{project_dir}/vocals.wav',
                                  convolution_window=convolution_window, silence_threshold=silence_threshold, force=True)
