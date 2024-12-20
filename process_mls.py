# process MLS data
from datasets import load_dataset
import json
import mauser
from progressbar import progressbar
from pathlib import Path
from scipy.io.wavfile import write

mls_dir = '/vol/mlusers/mbentum/mls/'

def load_mls(language):
    dataset = load_dataset("facebook/multilingual_librispeech", language)
    return dataset



def make_txt_file(item, split, language):
    txt_dir = f'{mls_dir}{language}/txt/'
    directory = f'{txt_dir}{split}/'
    Path(directory).mkdir(parents=True, exist_ok=True)
    text = item['transcript']
    file_id = item['id']
    filename = f'{file_id}.txt'
    filename = directory + filename
    with open(filename, 'w') as f:
        f.write(text)
    return filename

def make_audio_filename(item, split, language):
    speaker = item['speaker_id']
    chapter = item['chapter_id']
    file_id = item['id']
    wav_dir = f'{mls_dir}{language}/audio/'
    directory = f'{wav_dir}{split}/'
    Path(directory).mkdir(parents=True, exist_ok=True)
    path = f'{directory}{file_id}.wav'
    return path

def make_audio(item, audio_filename):
    array = item['audio']['array']
    sample_rate = item['audio']['sampling_rate']
    write(audio_filename, 16000, array)

def handle_item(item, split, language):
    txt_filename = make_txt_file(item, split, language)
    audio_filename = make_audio_filename(item, split,
        language)
    make_audio(item, audio_filename)
    return txt_filename, audio_filename

def handle_items(items, split, language):
    output = []
    filename =f'{mls_dir}{language}/{language}_{split}.json'
    for item in progressbar(items):
        txt_filename, audio_filename= handle_item(item,
            split, language)
        json_line = {"audio_filename": audio_filename, 
            "text_filename": txt_filename}
        output.append(json_line)
    save_output(output, filename)
    return output

def handle_language(language, items = None,
    splits = ['dev', 'test', 'train']):
    if not items:
        items = load_mls(language)
    for key in splits:
        print(f'handling {key}')
        split = items[key]
        handle_items(split, key, language)




def save_output(output, output_file):
    with open(output_file, 'w') as f:
        json.dump(output, f)


def load_files(json_filename):
    with open(json_filename) as f:
        files= json.load(f)
    return files

    
def handle_force_align(language, splits = ['dev', 'test', 'train']):
    textgrid_dir = f'{mls_dir}{language}/textgrid/'
    if language == 'dutch': language_code = 'nld-NL'
    if language == 'polish': language_code = 'pol-PL'
    if language == 'english': language_code = 'eng-US'
    if language == 'german': language_code = 'deu-DE'
    for key in splits:
        print(f'handling {key} {language}, {language_code}')
        files=load_files(f'{mls_dir}{language}/{language}_{key}.json')
        textgrid_dir=f'{mls_dir}{language}/textgrid/{key}/'
        Path(textgrid_dir).mkdir(parents=True, exist_ok=True)
        p = mauser.Pipeline(files, textgrid_dir, language = language_code)
        p.run()

def force_align_dutch(splits = ['dev', 'test', 'train']):
    handle_force_align('dutch', splits)

def force_align_polish(splits = ['dev', 'test', 'train']):
    handle_force_align('polish', splits)

def force_align_english(splits = ['dev', 'test']):
    handle_force_align('english', splits)

def force_align_german(splits = ['dev', 'test']):
    handle_force_align('german', splits)

    
    
    
