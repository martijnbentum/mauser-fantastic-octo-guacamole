# process MLS data
from datasets import load_dataset
import json
import mauser
from pathlib import Path

txt_dir = '/Users/martijn.bentum/Documents/dev_mls/txt/'
wav_dir = '/Users/martijn.bentum/Documents/dev_mls/audio/'
textgrid_dir = '/Users/martijn.bentum/Documents/dev_mls/textgrid/'

def load_dutch():
    dataset = load_dataset("facebook/multilingual_librispeech", "dutch")
    return dataset

def load_dev_dutch():
    dutch = load_dutch()
    return dutch['dev']

def make_txt_file(item, directory = '../mls_dutch_dev_txt/'):
    Path(directory).mkdir(parents=True, exist_ok=True)
    text = item['transcript']
    file_id = item['id']
    filename = f'{file_id}.txt'
    path = directory + filename
    with open(path, 'w') as f:
        f.write(text)
    return filename

def make_audio_filename(item):
    speaker = item['speaker_id']
    chapter = item['chapter_id']
    file_id = item['id']
    path = f'{wav_dir}{speaker}/{chapter}/{file_id}.wav'
    return path

def handle_item(item):
    filename = make_txt_file(item)
    txt_filename = f'{txt_dir}{filename}'
    audio_filename = make_audio_filename(item)
    return txt_filename, audio_filename

def handle_items_dutch_dev(dutch_dev = None,output_file = '../dutch_dev.json'):
    if not dutch_dev: dutch_dev = load_dev_dutch()
    output = []
    for item in dutch_dev:
        txt_filename, audio_filename= handle_item(item)
        json_line = {"audio_filename": audio_filename, 
            "text_filename": txt_filename}
        output.append(json_line)
    with open(output_file, 'w') as f:
        json.dump(output, f)
    return output


def load_files():
    with open('/Users/martijn.bentum/Documents/dev_mls/dutch_dev.json') as f:
        files= json.load(f)
    return files

def make_force_align_pipeline(files = None):
    if not files: files = load_files()
    p = mauser.Pipeline(files, textgrid_dir, language = 'nld-NL')
    return p
    



    
    
    
