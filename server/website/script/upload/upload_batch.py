import os.path
import glob
import numpy as np
import requests


class ResultUploader(object):

    SUMMARY_EXT = '.summary'
    PARAMS_EXT = '.params'
    METRICS_EXT = '.metrics'
    SAMPLES_EXT = '.samples'
    EXPCFG_EXT = '.expconfig'
    RAW_EXT = '.csv'

    REQ_EXTS = [SUMMARY_EXT, PARAMS_EXT, METRICS_EXT, SAMPLES_EXT, EXPCFG_EXT]

    def __init__(self, upload_code, upload_url):
        self._upload_code = upload_code
        self._upload_url = upload_url

    def upload_batch(self, directories, max_files=5):
        for d in directories:
            cluster_name = os.path.basename(d)
            fnames = glob.glob(os.path.join(d, '*.summary'))
            if max_files < len(fnames):
                fnames = list(np.random.choice(fnames, max_files))
            bases = [fn.split('.summary')[0] for fn in fnames]

            # Verify required extensions exist
            for base in bases:
                print(base)
                complete = True
                for ext in self.REQ_EXTS:
                    next_file = base + ext
                    if not os.path.exists(next_file):
                        print("WARNING: missing file {}, skipping...".format(next_file))
                        complete = False
                        break
                if complete:
                    self.upload(base, cluster_name)

    def upload(self, basepath, cluster_name):
        exts = list(self.REQ_EXTS)
        if os.path.exists(basepath + self.RAW_EXT):
            exts.append(self.RAW_EXT)
        fhandlers = {ext: open(basepath + ext, 'rb') for ext in exts}
        params = {
            'summary_data': fhandlers[self.SUMMARY_EXT],
            'db_metrics_data': fhandlers[self.METRICS_EXT],
            'db_parameters_data': fhandlers[self.PARAMS_EXT],
            'sample_data': fhandlers[self.SAMPLES_EXT],
            'benchmark_conf_data': fhandlers[self.EXPCFG_EXT],
        }

        if self.RAW_EXT in fhandlers:
            params['raw_data'] = fhandlers[self.RAW_EXT]

        response = requests.post(self._upload_url,
                                files=params,
                                data={'upload_code': self._upload_code,
                                      'cluster_name': cluster_name})
        print(response)

        for fh in fhandlers.values():
            fh.close()

def main():
    url = 'http://0.0.0.0:8000/new_result/'
    upload_code = 'O50GE1HC8S1BHU8L6F8D'
    uploader = ResultUploader(upload_code, url)
    dirnames = glob.glob(os.path.join(os.path.expanduser('~'), 'Dropbox/Apps/ottertune/data/sample_data/exps_*'))[:2]
    #order = np.random.choice(np.arange(len(dirnames)), len(dirnames))
    #dirnames = [dirnames[i] for i in order]
    uploader.upload_batch(dirnames, max_files=3)

if __name__ == '__main__':
    main()
