import os.path
from pathlib import Path


def replace_audio_track_in_video(video_mp4, accompaniment_mp3, suffix="-accompaniment", force=False):
    project_dir = os.path.abspath(os.path.dirname(video_mp4))
    video_accompaniment_mp4 = os.path.abspath(f"{project_dir}/{Path(os.path.basename(video_mp4)).stem}{suffix}.mp4")
    if os.path.exists(video_accompaniment_mp4):
        if force:
            os.remove(video_accompaniment_mp4)
        else:
            return video_accompaniment_mp4
    os.system(f'ffmpeg -i {video_mp4} -i {accompaniment_mp3} -c:v copy -map 0:v:0 -map 1:a:0 {video_accompaniment_mp4}')
    return video_accompaniment_mp4

if __name__ == '__main__':
    from projects import get_project_dir, get_project_data
    project_name = 'hudson-hawk-swinging-on-a-star'
    project_name = 'afi-medicate'
    project_dir = get_project_dir(project_name)
    replace_audio_track_in_video(f'{project_dir}/video-accompaniment.mp4', f'{project_dir}/accompaniment-with-choirs.mp3', "-with-choirs", force=True)
