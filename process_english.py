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
    p = mauser.Pipeline(files, textgrid_directory, language = None, 
        language_dict = make_accent_dict())
    return p
    

def make_accent_dict():
    t = load_validated()
    d = {}
    for line in t[1:]:
        if line == '': continue
        line = line.split('\t')
        sentence_id = line[1]
        accent = line[-1]
        if accent == '': accent = 'eng-US'
        if accent == 'newzealand': accent = 'eng-NZ'
        if accent == 'wales': accent = 'eng-GB'
        if accent == 'malaysia': accent = 'eng-US'
        if accent == 'indian': accent = 'eng-GB'
        if accent == 'australia': accent = 'eng-AU'
        if accent == 'bermuda': accent = 'eng-US'
        if accent == 'philippines': accent = 'eng-US'
        if accent == 'us': accent = 'eng-US'
        if accent == 'southatlandtic': accent = 'eng-US'
        if accent == 'hongkong': accent = 'eng-GB'
        if accent == 'african': accent = 'eng-GB'
        if accent == 'singapore': accent = 'eng-US'
        if accent == 'canada': accent = 'eng-US'
        if accent == 'other': accent = 'eng-US'
        if accent == 'ireland': accent = 'eng-GB'
        if accent == 'scotland': accent = 'eng-SC'
        if accent == 'england': accent = 'eng-GB'
        d[sentence_id] =accent
    return d
