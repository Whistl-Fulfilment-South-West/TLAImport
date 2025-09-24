
from csvfile import *
from error import *
from xmlcreation import *
from datetime import datetime
from exportxml import *
import numpy as np
import sys
from db import *

def cust_transform(df,folder):
    #get a list of "has customer" rows
    has_customer = 'CUSTOMER' in df.columns and df['CUSTOMER'].notna() & df['CUSTOMER'].astype(str).str.strip().ne('')

    #Get list of address columns (columns starting with "ADDRESS")
    address_cols = [col for col in df.columns if col.upper().startswith('ADDRESS')]
    # get list of "doesn't have address" rows
    if address_cols:
      # Consider a row "missing address" if ALL address columns are blank
        no_address = df[address_cols].apply(lambda row: all(
            pd.isna(val) or str(val).strip() == '' for val in row
        ), axis=1)
    else:
        # No address-like columns exist at all, all rows must have their address checked
        no_address = pd.Series([True] * len(df), index=df.index)

    # Combine conditions
    result = df[has_customer & no_address]

    #if we have any results, we need to get a client and try to find the customer details
    if not result.empty:
        #get client based on folder or user input
        client = get_client(folder)

        # Modify the result rows
        modified = result.apply(lambda row: get_addr(row, client), axis=1)

        #make sure all columns are in the original df, update with details from above query
        for col in modified.columns:
            if col not in df.columns:
                df[col] = None
        df.update(modified)

    return df
    

def main(source = None, client = None,automated = 0,prefix = None,logkeep = 30):
    #if source not defined, error out immediately
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
        logclear(log_dest,logkeep)
        
     
        #Find webimport folder if client specified
        webimport = None
        if client != None:
            if client.startswith("\\\\") or client.startswith("C:\\"):
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
            if automated == 0:
                raise Exception(f"No CSV files found in {source}")
            else:
                print("Exiting Program")
                sys.stdout = old_stdout
                log_file.close()
                sys.exit()


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
            
            #Do the customer no/address checks at row level
            df = cust_transform(df,source)

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
                
                #Add prefix if it exists
                if prefix is not None:
                    o = f"{prefix}{o}"  
                    of = of.copy()  
                    of["REF_NO"] = prefix + of["REF_NO"].astype(str)
                  
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
            if automated == 0:
                mess_display(f"Exporting XML files to {webimport}")
            exported = expml(dest,webimport,log_file)
            if exported == 1:
                raise Exception("Permission denied for XML destination folder - Please contact IS")
            elif exported == 2:
                raise Exception("Error exporting XML. Please check log.")

    
        print(f"{datetime.now()}: All tasks complete, closing")

    except PermissionError as e:
        print(f"{datetime.now()}: PERMISSION ERROR - {e}")
        if automated == 0:
            err_display("Permission error - file open or permission denied")
    
    except Exception as e:
        print(f"{datetime.now()}: ERROR - {e}")
        if automated == 0:
            err_display(e)

    finally:
        #close logging
        sys.stdout = old_stdout
        log_file.close()
        
#argument order (update 01.09.2025)     
#1. Source - where the CSV file should be - no default, this is needed.
#2. Destination - where the XML file will go - default NONE, will be kept in source folder/ORD/IN
#3. Display suppression - if this is "suppressdisplay", no messages will be displayed (for automation). Default NONE, messages will be displayed.
#4. Prefix - this will be added to the start of any order numbers if it exists. Default NONE, nothing will be added.
#5. Log keep - how long in days the log files will be kept for. Anything older than this will be deleted the next time the process is ran. Default 30.


if __name__ == "__main__":
    if len(sys.argv) == 6:
        source = sys.argv[1]
        client = sys.argv[2]
        if sys.argv[3] == "suppressdisplay":
            automate = 1
        else:
            automate = 0
        prefix = sys.argv[4]
        logkeep = sys.argv[5]
        main(source,client,automate,prefix,logkeep)
        sys.exit()
    elif len(sys.argv) == 5:
        source = sys.argv[1]
        client = sys.argv[2]
        if sys.argv[3] == "suppressdisplay":
            automate = 1
        else:
            automate = 0
        prefix = sys.argv[4]
        main(source,client,automate,prefix)
        sys.exit()
    elif len(sys.argv) == 4:
        source = sys.argv[1]
        client = sys.argv[2]
        if sys.argv[3] == "suppressdisplay":
            automate = 1
        else:
            automate = 0
        main(source,client,automate)
        sys.exit()
    elif len(sys.argv) == 3:
        source = sys.argv[1]
        client = sys.argv[2]
        main(source,client)
        sys.exit()
    elif len(sys.argv) == 2:
        source = sys.argv[1]
        client = None
        main(source)
        sys.exit()
    elif len(sys.argv) > 6:
        err_display("Shortcut has too many arguments. Please contact IS.")
    else:
        main("C:/Development/python/xmlorderimport")