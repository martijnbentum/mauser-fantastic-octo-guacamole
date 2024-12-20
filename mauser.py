import connector
import json
from lxml import etree
from pathlib import Path
from progressbar import progressbar
import subprocess
import threading
import time
import datetime


class Pipeline:
    def __init__(self, files, output_directory, language,  
        output_format = 'TextGrid', pipe = 'G2P_MAUS_PHO2SYL', preseg = 'true',
        language_dict = None):
        
        self.files= files
        self.output_directory = output_directory
        self.language = language
        self.output_format = output_format
        self.pip = pipe
        self.preseg = preseg
        self.language_dict = language_dict
        self.data = connector.create_data_dict(language, output_format, 
            pipe, preseg)
        self.done = []
        self.responses = []
        self.skipped = []
        self.error = []
        self.executers = []
        self.wait_time = 1

    def __repr__(self):
        m = 'language: ' + self.data['LANGUAGE']
        m += ' | output_format: ' + self.data['OUTFORMAT']
        m += ' | pipe: ' + self.data['PIPE']
        m += ' | preseg: ' + self.data['PRESEG']
        return m

    def remove_finished_executers(self):
        temp = []
        for executer in self.executers:
            if executer.is_alive():
                temp.append(executer)
        self.executers = temp

    def check_executers(self):
        self.remove_finished_executers()
        if len(self.executers) > 6:
            print('\nwaiting for executers to finish\n',datetime.datetime.now())
        self.start = time.time()
        self.do_restart = False
        while len(self.executers) > 6:
            time.sleep(1)
            self.remove_finished_executers()
            if self.start + 1200 < time.time():
                self.do_restart = True
                print('timeout, waiting to long for executers to finish')
                raise KeyboardInterrupt
                break
        if self.do_restart:
            print('restarting')
            self.run()


    def run(self):
        for line in progressbar(self.files):
            audio_filename = line['audio_filename']
            output_filename = connector.make_output_filename(
                self.output_directory,audio_filename, self.output_format)
            if Path(output_filename).exists(): 
                self.skipped.append(output_filename)
                continue
            self.check_executers()
            d = {'line': line}
            e = threading.Thread(target= self._run_single,kwargs=d)
            e.start()
            self.executers.append(e)
            time.sleep(self.wait_time)
                
            #self._run_single(line)

    def _run_single(self, line):
        line.update(self.data)
        if self.language_dict:
            sentence_id =  Path(line['audio_filename']).stem
            accent = self.language_dict[sentence_id]
            line['LANGUAGE'] = accent
        line['output_directory'] = self.output_directory
        result = run_command(line)
        message = result.stdout.decode()
        print(message, line['audio_filename'])
        if 'output exists' in message:
            self.skipped.append(line['audio_filename'], message)
        elif 'error' in message:
            self.error.append([line['audio_filename'], message])
        if 'saved' in message:
            self.done.append(line['audio_filename'])



        
    def _make_output_filename(self, filename):
        name = Path(filename).stem
        return self.output_directory + name + '.' + self.output_format

    def check_load(self):
        self.load = get_load_indicator()
        while self.load == None or self.load.load > 1:
            time.sleep(5)
            self.load = get_load_indicator()
        if self.load.load == 0: self.wait_time = 1
        if self.load.load == 1: self.wait_time = 3

    def check_executers(self):
        self.remove_finished_executers()
        if len(self.executers) > 6:
            print('\nwaiting for executers to finish\n',datetime.datetime.now())
        while len(self.executers) > 6:
            time.sleep(1)
            self.remove_finished_executers()

    def remove_finished_executers(self):
        temp = []
        for executer in self.executers:
            if executer.is_alive():
                temp.append(executer)
        self.executers = temp


def run_command(args):
    cmd = 'python3 connector.py ' 
    cmd += args['audio_filename'] 
    cmd += ' ' + args['text_filename']
    cmd += ' ' + args['output_directory']
    cmd += ' ' + args['LANGUAGE'] 
    cmd += ' --output_format ' + args['OUTFORMAT']
    cmd += ' --pipe ' + args['PIPE'] 
    cmd += ' --preseg ' + args['PRESEG']
    print(cmd)
    result = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
    return result




        
    
            




