import os

src_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.environ["DATA_DIR"] if "DATA_DIR" in os.environ else f'{os.path.dirname(__file__)}/../data'
output_dir = os.environ["OUTPUT_DIR"] if "OUTPUT_DIR" in os.environ else f'{os.path.dirname(__file__)}/../output'
media_dir = os.environ["MEDIA_DIR"] if "MEDIA_DIR" in os.environ else f'{os.path.dirname(__file__)}/../media'
webapp_dir = f'{src_dir}/../karaoke-app/karaoke-web/dist'
resources_dir = f'{src_dir}/../resources'