# process MLS data
from datasets import load_dataset
import json
import mauser
from progressbar import progressbar
from pathlib import Path
from scipy.io.wavfile import write

mls_dir = '/vol/mlusers/mbentum/mls/'

def load_mls(language):
    if language == 'english':
        dataset = load_dataset("parler-tts/mls_eng")
    else:
        dataset = load_dataset("facebook/multilingual_librispeech", language)
    return dataset

def make_txt_file(item, split, language):
    txt_dir = f'{mls_dir}{language}/txt/'
    directory = f'{txt_dir}{split}/'
    Path(directory).mkdir(parents=True, exist_ok=True)
    text = item['transcript']
    if language == 'english':
        file_id = item['audio']['path'].split('.')[0]
    else:
        file_id = item['id']
    filename = f'{file_id}.txt'
    filename = directory + filename
    with open(filename, 'w') as f:
        f.write(text)
    return filename

def make_audio_filename(item, split, language):
    speaker = item['speaker_id']
    if language == 'english':
        file_id = item['audio']['path'].split('.')[0]
        chapter = item['book_id']
    else:
        file_id = item['id']
        chapter = item['chapter_id']
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

def handle_items(items, split, language, start = None,
    end = None):
    output = []
    filename =f'{mls_dir}{language}/{language}_{split}.json'
    index = 0
    for item in progressbar(items):
        if start is None: pass
        elif index < start:
            index += 1
            continue 
        txt_filename, audio_filename= handle_item(item,
            split, language)
        json_line = {"audio_filename": audio_filename, 
            "text_filename": txt_filename}
        output.append(json_line)
        if end is None: pass
        elif index >= end:
            break
    save_output(output, filename)
    return output

def handle_language(language, items = None,
    splits = ['dev', 'test', 'train'], 
    start = None, end = None):
    if not items:
        items = load_mls(language)
    for key in splits:
        print(f'handling {key}')
        split = items[key]
        handle_items(split, key, language, start,end)


def handle_css10_hungarian():
    directory = '/vol/mlusers/mbentum/mls/hungarian/'
    with open(f'{directory}transcript.txt') as f:
        t = f.read().split('\n')
    output = []
    for line in t:
        f, transcript,_,_ = line.split('|')
        f = f.split('/')[-1]
        text_filename = Path(f'{directory}txt/test/' + f.replace('wav','txt'))
        audio_filename = Path(f'{directory}audio/test/'+ f)
        o = {'audio_filename':str(audio_filename),
            'text_filename':str(text_filename)}
        output.append(o)
        with open(str(text_filename), 'w') as f:
            f.write(transcript)
        if not text_filename.exists():
            raise Exception(f'{text_filename} does not exist')
        if not audio_filename.exists():
            raise Exception(f'{audio_filename} does not exist')
        # print(f,text_filename,'\n',o,transcript)
    save_output(output, f'{directory}hungarian_test.json')


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
    if language == 'hungarian': language_code = 'hun-HU'
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

def force_align_hungarian(splits = ['test']):
    handle_force_align('hungarian', splits)

    
    
    
