# Description: This script processes the common voice Polish dataset.
# creates forced alignments   

import json
import glob
import mauser
from pathlib import Path

directory = '../../LD/COMMON_VOICE_POLISH/'
textgrid_directory = directory + 'textgrids/'
audio_directory = directory + 'clips/'
transcription_directory = directory + 'transcriptions/'

def load_validated():
    with open(directory + 'validated.tsv', 'r') as f:
        t = f.read().split('\n')
    return t

def make_transcription_files():
    t = load_validated()
    for line in t[1:]:
        if line == '': continue
        line = line.split('\t')
        text = line[3].strip('" ')
        filename = directory + 'transcriptions/' + line[1].replace('.mp3','.txt')
        with open(filename, 'w') as f:
            f.write(text)
    
def make_files(force_make = False):
    if not force_make and Path('polish_files.json').exists():
        with open('polish_files.json', 'r') as f:
            files = json.load(f)
        return files
    audio_filenames = glob.glob(audio_directory + '*.mp3')
    text_filenames = glob.glob(transcription_directory + '*.txt')
    files = mauser.Files(audio_filenames, text_filenames, 'polish_files.json')
    return files.files

def make_force_align_pipeline():
    files = make_files()
    p = mauser.Pipeline(files, textgrid_directory)
    return p
    
