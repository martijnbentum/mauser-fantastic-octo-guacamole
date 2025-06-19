# Description: This script processes the common voice Polish dataset.
# creates forced alignments   

import glob
import file_matcher
import json
import mauser
from pathlib import Path

directory = '../cgn/comp-o/'
textgrid_directory = directory + 'textgrids/'
transcription_directory = directory + 'transcriptions/'

def make_files():
    with open('../cgn/file_map_o.json') as f:
        file_map= json.load(f)
    files = []
    for cgn_id, audio_filename in file_map.items():
        f = transcription_directory + cgn_id + '.txt'
        d = {'audio_filename': audio_filename, 'text_filename': f}
        files.append(d)
    return files

def make_force_align_pipeline(files = None):
    if not files: files = make_files()
    p = mauser.Pipeline(files, textgrid_directory, language = 'nld-NL',
        pipe = 'G2P_CHUNKER_MAUS_PHO2SYL')
    return p
    
