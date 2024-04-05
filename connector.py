import argparse
import json
from lxml import etree
from pathlib import Path
import requests
from requests.exceptions import ConnectionError
import url

def get_load_indicator():
    load_indicator = url.load_indicator
    try:
        response = requests.get(load_indicator)
    except ConnectionError as e:
        print('ConnectionError load indicator')
        return None
    return Response(response)

def check_load():
    load = get_load_indicator()
    while load == None or load.load > 1:
        time.sleep(5)
        load = get_load_indicator()
    return load

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
    try: response = requests.post(pipeline, files=files, data=data)
    except ConnectionError as e:
        print('ConnectionError pipeline')
        response = None
    close_files(files)
    if response == None: return None
    return Response(response)


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
        self.load = int(self.content)

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
        self.download_connection_ok = None
        if self.success and self.type == 'pipeline':
            try:
                self.download_response = requests.get(self.download_link)
                self.download_output = self.download_response.content.decode()
                self.download_connection_ok = True
            except ConnectionError as e:
                print('ConnectionError')#, print(e))
                self.download_connection_ok = False
                self.response.download_connection_error = e
            except Exception as e:
                self.response.download_error = e
        return self.download_output

def save_output(output, filename):
    with open(filename, 'w') as f:
        f.write(output)

def create_files_dict(audio_filename, text_filename):
    return {'SIGNAL': open(audio_filename, 'rb'), 
        'TEXT': open(text_filename, 'rb')}

def close_files(files):
    for f in files.values():
        f.close()

def create_data_dict(language, output_format = 'TextGrid', 
    pipe = 'G2P_MAUS_PHO2SYL',preseg = True):
    return {'LANGUAGE': language,
            'OUTFORMAT': output_format,
            'PRESEG': preseg,
            'PIPE': pipe,
            }

def make_output_filename(output_directory, filename, output_format):
    name = Path(filename).stem
    return output_directory + name + '.' + output_format

def _handle_pipeline_run(args):
    output_filename = make_output_filename(args.output_directory, 
        args.audio_filename, args.output_format)
    if Path(output_filename).exists(): 
        print('output exists error')
        return 
    response = run_pipeline(args.audio_filename, args.text_filename,
        args.language, args.output_format, args.pipe, args.preseg)
    if response != None and response.success: 
        output = response.download()
        if output:
            save_output(output, output_filename)
            print('saved:', output_filename)
        else: print('download error')
    else: print('response error')

def _main():
    description = 'interact with bas web services'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('audio_filename', help='path to audio file')
    parser.add_argument('text_filename', help='path to text file')
    parser.add_argument('output_directory', help='directory to save output')
    parser.add_argument('language', help='language code')
    parser.add_argument('--output_format', help='output format', 
        default='TextGrid')
    parser.add_argument('--pipe', help='pipeline', 
        default='G2P_MAUS_PHO2SYL')
    parser.add_argument('--preseg', help='presegmentation',
        default='true')
    args = parser.parse_args()
    return _handle_pipeline_run(args)

if __name__ == '__main__':
    _main()
