import json
from lxml import etree
from pathlib import Path
from progressbar import progressbar
import requests
import threading
import url


class Pipeline:
    def __init__(self, files, output_directory, language = 'pol-PL', 
        output_format = 'TextGrid', pipe = 'G2P_MAUS_PHO2SYL', preseg = 'true'):
        
        self.files= files
        self.language = language
        self.output_format = TextGrid
        self.pip = pipe
        self.preseg = preseg
        self.data = create_data_dict(language, output_format, pipe, preseg)
        self.done = []
        self.responses = []
        self.skipped = []
        self.error = []

    def __repr__(self):
        m = 'language: ' + self.data['LANGUAGE']
        m += ' | output_format: ' + self.data['OUTFORMAT']
        m += ' | pipe: ' + self.data['PIPE']
        m += ' | preseg: ' + self.data['PRESEG']
        return m

    def run(self):
        for line in self.files:
            if line['audio_filename'] in self.done: continue
            self.check_load()            
            self._run_single(**files)

    def _run_single(self, audio_filename, text_filename)
        output_filename = self._make_output_filename(audio_filename)
        if Path(output_filename).exists(): 
            self.skipped(output_filename)
            if audio_filename not in self.done: self.done.append(audio_filename)
            return
        files = create_files_dict(audio_filename, text_filename)
        response = _run_pipeline(files, self.data)
        response = Response(response)
        if response.success: 
            output = response.download()
            self.responses.append(response)
            save_output(output, output_filename)
        else: self.error.append(response)
        
    def _make_output_filename(self, filename):
        name = path(filename).stem
        return self.output_directory + name + output_format




class Response:
    def __init__(self, response):
        self.response = response
        self.content = response.content.decode()
        if self.content in ['0','1','2']:
            self._handle_load_indicator_response()
        if 'downloadLink' in self.content:
            self._handle_pipeline_response()

    def __repr__(self):
        m = self.type 
        if self.type == 'load_indicator':
            m += ' | load: ' + str(self.load)
        if self.type == 'pipeline':
            m += ' | success: ' + str(self.success)
            m += ' | output_filename: ' + self.output_filename
        return m

    def _handle_load_indicator_response(self):
        self.type = 'load_indicator'
        self.load = int(self.raw)

    def _handle_pipeline_response(self):
        self.type = 'pipeline'
        self.xml = etree.fromstring(self.content)
        self.success = True if self.xml.find('success').text == 'true' else False
        self.download_link = self.xml.find('downloadLink').text
        self.output_filename = self.download_link.split('/')[-1]
        self.output = self.xml.find('output').text
        self.warnings = self.xml.find('warnings').text
            
    def download(self):
        if hasattr(self,'download_output'):
            return self.download_output
        self.download_output = None
        if self.success and self.type == 'pipeline':
            self.download_response = requests.get(self.download_link)
            self.download_output = self.download_response.content.decode()
        return self.download_output

class Files():
    def __init__(self, audio_filenames, text_filenames, filename = ''):
        self.audio_filenames = [Path(f) for f in audio_filenames]
        self.text_filenames = [Path(f) for f in text_filenames]
        self._make_files()
        if filename:
            self._save(filename)
        
    def __repr__(self):
        m = 'Data | ' + str(len(self.datas)) + ' files'
        return m

    def _make_files(self):
        self.files= []
        for af in progressbar(self.audio_filenames[:100]):
            for tf in self.text_filenames:
                if af.stem== tf.stem:
                    d = {'audio_filename':str(af),
                        'text_filename':str(tf)}
                    self.files.append(d)
                    break

    def _save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.files, f)


        
    
            
def run_g2p_maus_phon2syl(audio_filename, text_filename, language, 
    output_format = 'TextGrid', preseg = 'true'):
    return run_pipeline(audio_filename, text_filename, language, output_format,
        'G2P_MAUS_PHO2SYL', preseg)

def run_pipeline(audio_filename, text_filename, language, 
    output_format = 'TextGrid', pipe = 'G2P_MAUS_PHO2SYL', preseg = 'true'):
    files = create_files_dict(audio_filename, text_filename)
    data = create_data_dict(language, output_format, pipe, preseg)
    return _run_pipeline(files, data)

def _run_pipeline(files, data):
    pipeline = url.pipeline
    response = requests.post(pipeline, files=files, data=data)
    return Response(response)

def create_files_dict(audio_filename, text_filename):
    return {'SIGNAL': open(audio_filename, 'rb'), 
        'TEXT': open(text_filename, 'rb')}

def create_data_dict(language, output_format = 'TextGrid', 
    pipe = 'G2P_MAUS_PHO2SYL',preseg = True):
    return {'LANGUAGE': language,
            'OUTFORMAT': output_format,
            'PRESEG': preseg,
            'PIPE': pipe,
            }

def get_load_indicator():
    load_indicator = url.load_indicator
    response = requests.get(load_indicator)
    return Response(response)

