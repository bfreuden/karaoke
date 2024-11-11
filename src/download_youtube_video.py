import os.path

from pytube import YouTube

pytube_patched = False

def maybe_patch_pytube():
    global pytube_patched
    if pytube_patched:
        return
    pytube_patched = True
    import ssl
    from pytube.innertube import _default_clients
    from pytube.exceptions import RegexMatchError

    _default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
    _default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
    _default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
    _default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
    _default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
    _default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID"]

    import pytube, re
    def patched_get_throttling_function_name(js: str) -> str:
        function_patterns = [
            r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
            r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
            r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
        ]
        for pattern in function_patterns:
            regex = re.compile(pattern)
            function_match = regex.search(js)
            if function_match:
                if len(function_match.groups()) == 1:
                    return function_match.group(1)
                idx = function_match.group(2)
                if idx:
                    idx = idx.strip("[]")
                    array = re.search(
                        r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                            nfunc=re.escape(function_match.group(1))),
                        js
                    )
                    if array:
                        array = array.group(1).strip("[]").split(",")
                        array = [x.strip() for x in array]
                        return array[int(idx)]

        raise RegexMatchError(
            caller="get_throttling_function_name", pattern="multiple"
        )

    ssl._create_default_https_context = ssl._create_unverified_context
    pytube.cipher.get_throttling_function_name = patched_get_throttling_function_name


def download_youtube_video(youtube_url, output_dir, force=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = f'{output_dir}/video.mp4'
    if os.path.exists(output_file) and not force:
        return output_file
    maybe_patch_pytube()
    YouTube(youtube_url).streams \
        .filter(progressive=True, file_extension='mp4') \
        .order_by('resolution') \
        .desc() \
        .first() \
        .download(output_path=os.path.dirname(output_file), filename=os.path.basename(output_file))
    return output_file

if __name__ == '__main__':
    from get_or_create_karaoke_project_data import get_project_dir
    youtube_url = 'https://www.youtube.com/watch?v=huMElOuIMmk'
    project_dir = get_project_dir(youtube_url)
    download_youtube_video(youtube_url, project_dir, force=True)
