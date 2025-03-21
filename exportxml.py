import pypyodbc 
import pandas as pd
import os
from os import listdir
from datetime import datetime
import sys
import shutil

def find_webimport(client):
    try:
        cnxn = pypyodbc.connect(
            "Driver={SQL Server Native Client 11.0};"
            "Server=SQL-SSRS;"
            "Database=Appz;"
            "Integrated Security=true;"
            "Trusted_Connection=Yes"
        )

        # Use parameterized query to prevent SQL injection
        query = "SELECT folder FROM tla_connect WHERE client = ?"
        ff = pd.read_sql_query(query, cnxn, params=[client])

        # Close connection
        cnxn.close()

        # Return the folder if found
        if not ff.empty:
            print(f'{datetime.now()}: Files to be sent to {str(ff["folder"].values[0])}')
            return str(ff["folder"].values[0])
        else:
            print(f"{datetime.now()}: Client not found")
            return
    except Exception as e:
        print(f"Error: {e}")
        return 

def expml(source, dest, log, suffix=".xml"):
    try:
        filenames = listdir(source)
        xmlnames = [filename for filename in filenames if filename.endswith(suffix)]
        print(f"{datetime.now()}: {len(xmlnames)} xml files found, exporting")

        for x in xmlnames:
            print(f"{datetime.now()}: Exporting {x}")
            shutil.move(os.path.join(source, x), os.path.join(dest, x))
    
    except Exception as e:
        error_message = f"{datetime.now()}: ERROR - {str(e)}\n"
        sys.stderr = log
        sys.stderr.write(error_message)
        sys.stderr.flush()  # Ensure it writes immediately
    
if __name__ == "__main__":
    print(find_webimport("test"))