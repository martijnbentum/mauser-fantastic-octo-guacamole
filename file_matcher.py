import json
from pathlib import Path
from progressbar import progressbar

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
        for af in progressbar(self.audio_filenames):
            for tf in self.text_filenames:
                if af.stem== tf.stem:
                    d = {'audio_filename':str(af),
                        'text_filename':str(tf)}
                    self.files.append(d)
                    break
    def _save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.files, f)
