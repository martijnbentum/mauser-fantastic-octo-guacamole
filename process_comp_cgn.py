# Description: This script processes the spoken dutch corpus dataset.
# creates forced alignments   

import glob
import file_matcher
import json
import mauser
from pathlib import Path

def make_cgn_files_for_components(components = None):
    if not components: components = 'a,b,e,f,g,h,i,j,l,n'.split(',')
    files = []
    for component in components:
        print('handling component', component)
        files = make_files(component)
        p = make_force_align_pipeline(files, component)
        p.run()
        

def make_files(component):
    directory = f'../cgn/comp-{component}/'
    transcription_directory = directory + 'transcriptions/'
    filename = f'../cgn/file_map_{component}.json'
    with open(filename) as f:
        file_map= json.load(f)
    files = []
    for cgn_id, audio_filename in file_map.items():
        f = transcription_directory + cgn_id + '.txt'
        d = {'audio_filename': audio_filename, 'text_filename': f}
        files.append(d)
    return files

def make_force_align_pipeline(files, component):
    directory = f'../cgn/comp-{component}/'
    textgrid_directory = directory + 'textgrids/'
    p = mauser.Pipeline(files, textgrid_directory, language = 'nld-NL',
        pipe = 'G2P_CHUNKER_MAUS_PHO2SYL')
    return p
    
