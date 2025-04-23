import os
from os import listdir
from datetime import datetime
import sys
import shutil
from error import err_display


def expml(source, dest, log, automated, suffix=".xml"):
    try:
        filenames = listdir(source)
        xmlnames = [filename for filename in filenames if filename.endswith(suffix)]
        print(f"{datetime.now()}: {len(xmlnames)} xml files found, exporting")

        for x in xmlnames:
            print(f"{datetime.now()}: Exporting {x}")
            shutil.move(os.path.join(source, x), os.path.join(dest, x))

    except PermissionError:
        error_message = f"{datetime.now()}: permission for folder {dest} denied. Please contact IS.\n"
        if automated == 0:
            err_display(f"ERROR - {e}")
        sys.stderr = log
        sys.stderr.write(error_message)
        sys.stderr.flush()

    except Exception as e:
        error_message = f"{datetime.now()}: ERROR - {str(e)}\n"
        if automated == 0:
            err_display(f"ERROR - {e}")
        sys.stderr = log
        sys.stderr.write(error_message)
        sys.stderr.flush() 
    
