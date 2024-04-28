# Description: This script processes the common voice English dataset.
# creates forced alignments   

import glob
import file_matcher
import json
import mauser
from pathlib import Path

directory = '../../LD/COMMON_VOICE_ENGLISH/'
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
        text = line[2].strip('" ')
        filename = directory + 'transcriptions/' + line[1] + '.txt'
        with open(filename, 'w') as f:
            f.write(text)
    
def make_files(force_make = False):
    if not force_make and Path('english_files.json').exists():
        with open('english_files.json', 'r') as f:
            files = json.load(f)
        return files
    audio_filenames = glob.glob(audio_directory + '*.mp3')
    text_filenames = glob.glob(transcription_directory + '*.txt')
    files = file_matcher.Files(audio_filenames, text_filenames, 
        'english_files.json')
    return files.files

def make_force_align_pipeline(files = None):
    if not files: files = make_files()
    p = mauser.Pipeline(files, textgrid_directory, language = 'eng-EN')
    return p
    
