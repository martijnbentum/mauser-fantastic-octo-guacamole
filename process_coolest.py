import glob
import file_matcher
import json
import mauser
from pathlib import Path

root_directory = '/vol/tensusers/mbentum/INDEEP/LD/COOLEST/Recordings'
textgrid_directory='/vol/tensusers/mbentum/INDEEP/LD/COOLEST/mauser_textgrids/'

def get_audio_files():
    root_folder = Path(root_directory)
    audio_files = root_folder.glob('**/*.wav')
    return audio_files

def get_transcription_files():
    root_folder = Path(root_directory)
    textgrid_files = root_folder.glob('**/*.txt')
    return textgrid_files

def make_files(force_make = False):
    if not force_make and Path('coolest_files.json').exists():
        with open('coolest_files.json', 'r') as f:
            files = json.load(f)
        return files
    audio_filenames = get_audio_files()
    text_filenames = get_transcription_files()
    files = file_matcher.Files(audio_filenames, text_filenames, 
        'coolest_files.json')
    return files.files

def make_force_align_pipeline(files = None):
    if not files: files = make_files()
    p = mauser.Pipeline(files, textgrid_directory, language = 'nld-NL')
    return p
