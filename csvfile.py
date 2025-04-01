import pandas as pd
import os
import time
import glob
from datetime import datetime
from os import listdir
import chardet

def import_csv(path):
    return pd.read_csv(path, engine = "python",index_col = False)


    
def logclear(path, suffix = ".log"):
    for f in os.listdir(path):
        g = os.path.join(path, f)
        if g.endswith(suffix):
            if os.stat(g).st_mtime < time.time() - (30 * 86400):
                if os.path.isfile(g):
                    os.remove(g)

def getpath(source):
    extension = "csv"
    os.chdir(source)
    result = glob.glob('*.{}'.format(extension))
    print(result)


def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]


def archive_file(file,source,suffix = ".csv"):
    arch = source + "/done"
    ind = file.find(suffix)
    nufile = file[:ind] + datetime.now().strftime("%Y%m%dT%H%M%S") + file[ind:]
    os.makedirs(arch,exist_ok=True)
    os.rename(source + "/" + file, arch + "/" + nufile)


def detect_encoding(file_path, sample_size=1000):
    with open(file_path, 'rb') as f:
        raw_data = f.read(sample_size)
    result = chardet.detect(raw_data)
    return result['encoding']

# Convert to UTF-8 if necessary
def convert_to_utf8(input_file, output_file):
    encoding = detect_encoding(input_file)
    if encoding.lower() != 'utf-8':  # Convert only if not already UTF-8
        df = pd.read_csv(input_file, encoding=encoding, low_memory=False)
        df.to_csv(output_file, encoding='utf-8', index=False)
        print(f"{datetime.now()}: File converted from {encoding} to UTF-8")
    else:
        print(f"{datetime.now()}: File is already UTF-8 encoded")
