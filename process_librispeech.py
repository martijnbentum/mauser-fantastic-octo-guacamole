# Description: This script processes the librispeech dataset.
# creates forced alignments   

import glob
import file_matcher
import json
import mauser
from pathlib import Path
from progressbar import progressbar

librispeech_root = Path('/vol/bigdata/corpora2/Librispeech')
transcription_root = Path('../librispeech/token_transcriptions')
textgrid_root = Path('../librispeech/textgrids')

def make_transcriptions(partitions = ['dev-clean', 'train-clean'],):
    for partition in partitions:
        print('handling component', partition)
        files = make_files(partition)
        p = make_force_align_pipeline(files, partition)
        p.run()

def make_files(partition = 'dev-clean'):
    data = load_token_file(partition)
    files = []
    for identifier in data:
        audio_filename = str(file_id_to_wav_filename(identifier, partition))
        text_filename = str(file_id_to_text_filename(identifier, partition, data))
        d = {'audio_filename': audio_filename, 'text_filename': text_filename,}
        files.append(d)
    return files

def make_force_align_pipeline(files, partition = 'dev-clean'):
    textgrid_directory = str(textgrid_root) 
    if partition == 'dev-clean':
        textgrid_directory += '/dev/' 
    elif partition == 'train-clean':
        textgrid_directory += '/train/'
    else: raise ValueError('Unknown partition: ' + partition)
    if not Path(textgrid_directory).exists():
        raise ValueError('Textgrid directory does not exist: ' + textgrid_directory)
    p = mauser.Pipeline(files, textgrid_directory, language = 'eng-US',
        pipe = 'G2P_CHUNKER_MAUS')
    return p
    


def load_token_file(partition = 'dev-clean'):
    if partition == 'dev-clean':
        filename = '../librispeech/librispeech_dev-clean_tokenized.json'
    elif partition == 'train-clean':
        filename = '../librispeech/librispeech_train-clean-100_tokenized.json'
    else:
        raise ValueError('Unknown partition: ' + partition, 
            'use dev-clean or train-clean')
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def file_id_to_wav_filename(file_id, partition = 'dev-clean'):
    if partition == 'train-clean': partition = 'train-clean-100'
    d = librispeech_root / partition
    if not d.exists():
        raise ValueError('Partition does not exist: ' + str(d))
    directory = '/'.join(file_id.split('-')[:-1])
    filename = d / directory / (file_id + '.flac') 
    if not filename.exists():
        raise ValueError('File does not exist: ' + str(filename), file_id)
    return filename

def file_id_to_text_filename(file_id, partition = 'dev-clean', data = None):
    filename = transcription_root / (file_id + '.txt')
    if not filename.exists():
        tokens = file_id_to_tokens(file_id, partition, data)
        text = ' '.join(tokens)
        with open(filename, 'w') as f:
            f.write(text)
    if not filename.exists():
        raise ValueError('Text file does not exist: ' + str(filename), file_id)
    return filename

def file_id_to_tokens(file_id, partition = 'dev-clean', data = None):
    if data is None:
        data = load_token_file(partition)
    if file_id not in data:
        raise ValueError('File ID not found in token file: ' + file_id)
    return data[file_id]

def make_all_text_files():
    for partition in ['dev-clean', 'train-clean']:
        print('processing partition', partition)
        data = load_token_file(partition)
        for file_id in progressbar(data):
            _ = file_id_to_text_filename(file_id, partition, data)
    






