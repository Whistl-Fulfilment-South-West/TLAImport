import pandas as pd
import os
import glob
from datetime import datetime
from os import listdir

def import_csv(path):
    return pd.read_csv(path, engine = "python",index_col = False)
    

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



#df = import_csv("~/workspace/github.com/JimmyT64/xmlorderimport/test.csv")
#print(df.head())