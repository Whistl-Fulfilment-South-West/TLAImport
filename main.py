
from csvfile import *
from error import *
from xmlcreation import *
from datetime import datetime
from exportxml import *
import numpy as np
import sys




def main(source = None, client = None,automated = 0):
    #if source not defined, get the user to define it
    if source == None:
        err_display("Source location not defined in shortcut, please contact the IS team")
        sys.exit()

    try:
        
        #Make sure log folder exists, make it if not
        log_dest = source + f"/logs"
        os.makedirs(log_dest,exist_ok=True)
        
        #Organise logging
        old_stdout = sys.stdout
        log_file = open(log_dest + f"/log{datetime.now().strftime("%Y%m%dT%H%M%S")}.log","w")
        sys.stdout = log_file
        print(f"{datetime.now()}: Logging Start - {os.getenv("username")}")

        if automated == 1:
             print(f"{datetime.now()}: Automation active - no user-facing messages will be displayed")

        print(f"{datetime.now()}: Clearing old log files from {log_dest}")
        logclear(log_dest)
        
     
        #Find webimport folder if client specified
        webimport = None
        if client != None:
            if client.startswith("\\\\"):
                webimport = client
        #If failed, remove client so we don't try to move xmls
        if webimport == None:
            client = None

        if client == None:
            print(f"{datetime.now()}: Source Folder - {source}")
        else:
            print(f"{datetime.now()}: Source Folder - {source}, Destination folder - {webimport}")
        
        #Set initial destination folder based on source
        dest = source + "/ORD/IN"
    
        #Make sure destination folder exists
        os.makedirs(dest,exist_ok=True)

        print(f"{datetime.now()}: Checking for files in {source}")

        #list all csv files in source path
        list = find_csv_filenames(source)
        print(f"{datetime.now()}: {len(list)} files found")
        if len(list) == 0:
            raise Exception(f"No CSV files found in {source}")


        #import files seperately.
        for l in list:
            print(f"{datetime.now()}: Detecting encoding of {l}")
            convert_to_utf8(source +"/"+ l, source +"/"+ l)

            
            print(f"{datetime.now()}: Importing {l}")

            #import csv into dataframe
            df = import_csv(source +"/"+ l)

            #remove fields that are just a space, to prepare for the below
            df.replace(' ', np.nan, inplace=True)

            #Drop columns with no values in them
            df = df.dropna(axis = 1,how = 'all')

            #Drop rows with no values in them
            df = df.dropna(how = 'all')

            #initialise error column
            df["ERROR"] = ""

            #make all columns uppercase and remove spaces and underscores except for ref_no/ref no (to make checking they exist easier)
            df.columns = map(str.upper, df.columns)
            df.rename(columns={col: col.replace(" ", "_") for col in df.columns if col != "REF_NO"}, inplace=True)
            df.rename(columns={col: col.replace("_", "") for col in df.columns if col != "REF_NO"}, inplace=True)

            #rename common column misnomers
            df = renames(df)

            print(f"{datetime.now()}: Error checking on {l}")

            #run error checks/cleaning
            df = errorchex(df)

            #if any errors, export an errors file and go to next file in loop
            if df["ERROR"].any():
                print(f"{datetime.now()}: Errors found in {l}, exporting error file to {source}/errors")
                error_export(df,source,l)
                if automated == 0:
                    err_display(f"{datetime.now()}: Errors found in {l}, exporting error file to {source}/errors")
                continue

            print(f"{datetime.now()}: No errors found, checking for orders")

            #Get individual orders from dataframe
            grup = df.groupby("REF_NO")
            orders = grup.groups.keys()
            if len(orders) == 0:
                print(f"{datetime.now()}: No orders found, aborting import")
                if automated == 0:
                    err_display(f"No orders found in {l}")
                continue
            print(f"{datetime.now()}: {len(orders)} orders found in {l}")

            #confirm destination path exists, create it if not
            os.makedirs(dest,exist_ok=True)

            #Loop through orders and create xmls (Auto generated to destination path)
            for o in orders:
                if o == "":
                    continue
                of = df.loc[df["REF_NO"] == o]
                print(f"{datetime.now()}: Creating xml for order {o} in folder {dest}")
                err = xml_creation(o,of,dest)
                if err:
                    if automated == 0:
                        err_display(f"XML creation for order {o} failed, see log for details")
                    continue

            #Move CSV file to archive folder
            print(f"{datetime.now()}: Moving {l} to archive")
            archive_file(l,source)
            
        print(f"{datetime.now()}: XML creation completed")

        print(f"{datetime.now()}: Clearing down old archive files from {source}/done")
        archcleardown(source)

        #If no client specified, don't export XMLs
        if client == None:
            print(f"{datetime.now()}: No client specified, skipping webimport export")
            if automated == 0:
                mess_display("No webimport folder specified, please contact IS to move files")
        else:
        #else send XMLs to the webimport folder
            print(f"{datetime.now()}: exporting XML files to {webimport}")
            expml(dest,webimport,log_file,automated)
            if automated == 0:
                mess_display(f"Files exported to {webimport}")
    
        print(f"{datetime.now()}: All tasks complete, closing")

    except Exception as e:
        print(f"{datetime.now()}: ERROR - {e}")
        if automated == 0:
            err_display(e)

    finally:
        #close logging
        sys.stdout = old_stdout
        log_file.close()
        
        


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) == 4:
        source = sys.argv[1]
        client = sys.argv[2]
        if sys.argv[3] == "suppressdisplay":
            automate = 1
        else:
            automate = 0
        main(source,client,automate)
    elif len(sys.argv) == 3:
        source = sys.argv[1]
        client = sys.argv[2]
        main(source,client)
    elif len(sys.argv) == 2:
        source = sys.argv[1]
        client = None
        main(source)
    else:
        main()
    

