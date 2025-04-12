
sample_projects = {
    'dancing_in_the_dark': {
        'youtube_url': 'https://www.youtube.com/watch?v=huMElOuIMmk',
        'genius_url': 'https://genius.com/Amy-macdonald-dancing-in-the-dark-lyrics',
        'language': 'en',
        'model': 'stt_en_fastconformer_hybrid_large_pc',
    },
    'ma_direction': {
        'youtube_url': 'https://www.youtube.com/watch?v=Y7-vP7TnluY',
        'genius_url': 'https://genius.com/Sexion-dassaut-ma-direction-lyrics',
        'language': 'fr',
        'model': 'nvidia/stt_fr_fastconformer_hybrid_large_pc',
    },
    'criminal': {
        'youtube_url': 'https://www.youtube.com/watch?v=mR8_ldc9lag',
        'genius_url': 'https://genius.com/Eminem-criminal-lyrics',
        'language': 'en',
        'model': 'stt_en_fastconformer_hybrid_large_pc',
    },
    'afi_17_crimes': {
        'youtube_url': 'https://www.youtube.com/watch?v=Y9Vh8XGgqjE',
        'genius_url': 'https://genius.com/Afi-17-crimes-lyrics',
        'language': 'en',
        'model': 'stt_en_fastconformer_hybrid_large_pc',
    },
    'afi_medicate': {
        'youtube_url': 'https://www.youtube.com/watch?v=wCwEBz3ego8',
        'genius_url': 'https://genius.com/Afi-medicate-lyrics',
        'language': 'en',
        'model': 'stt_en_fastconformer_hybrid_large_pc',
        'speech_to_text_target': 'vocals'
    },
    'poets_standstill': {
        'youtube_url': 'https://www.youtube.com/watch?v=FsKxXnAoSDo',
        'genius_url': 'https://genius.com/Poets-of-the-fall-standstill-lyrics',
        'language': 'en',
        'model': 'stt_en_fastconformer_hybrid_large_pc',
    },
    'poets_dark_disquiet': {
        'youtube_url': 'https://www.youtube.com/watch?v=aMT5Tuw0yZk',
        'genius_url': 'https://genius.com/Poets-of-the-fall-my-dark-disquiet-lyrics',
        'language': 'en',
        'model': 'stt_en_fastconformer_hybrid_large_pc',
    },
}

from get_or_create_karaoke_project_data import get_project, get_project_dir

def get_sample_project(project_name):
    return get_project(sample_projects[project_name]['youtube_url'])

def get_sample_project_dir(project_name):
    return get_project_dir(get_sample_project(project_name)['youtube_url'])

def get_sample_project_items(project_name, *args):
    project = get_sample_project(project_name)
    return tuple(get_project_dir(project['youtube_url']) if arg == 'project_dir' else project[arg] for arg in args)
