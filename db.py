import numpy as np
import pandas as pd
import pyodbc
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk


def get_client(folder):
    print(f"{datetime.now()}: Querying preset folder list to find client for {folder}")
    conn = pyodbc.connect("DRIVER={SQL Server};SERVER=SQL-SSRS;DATABASE=Appz;Trusted_Connection=yes;")
    cursor = conn.cursor()
    sql = "SELECT clid FROM TLA_Folders WHERE folder = ?"
    try:
        cursor.execute(sql,folder)
        if cursor.rowcount == 0:
            print(f"{datetime.now()}: Failed to find {folder} in folder list, querying user")
            clid = clientchoose()
            if clid:
                print(f"{datetime.now()}: User chose {clid} as client, proceding with customer query")
                return clid
            else:
                print(f"{datetime.now()}: User did not choose client, and no client found in database. File will error.")
                return None
        return cursor.fetchone()[0]
    except pyodbc.DatabaseError:
        print(f"{datetime.now()}:ERROR: Cannot find client")
        return
    finally:
        #Close connections if they still exist
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_addr(row,clid):
    if clid == None:
        return row
    cust = row["CUSTOMER"]
    conn = pyodbc.connect("DRIVER={SQL Server};SERVER=SQL-SSRS;DATABASE=Appz;Trusted_Connection=yes;")
    cursor = conn.cursor()
    sql = "EXEC TLA_GetAddr ?,?"
    print(f"{datetime.now()}: Finding address for {cust} on {clid}")
    try:
        cursor.execute(sql,cust,clid)
        addr = cursor.fetchone()
        if addr == None:
            print(f"{datetime.now()}:No address found")
            return row
        print(f"{datetime.now()}: Address found")
        row["ADDRESS"] = addr[0]
        row["CITY"] = addr[1]
        row["POSTCODE"] = addr[2]
        row["FIRSTNAME"] = addr[3]
        row["SURNAME"] = addr[4]
        print(row)
        return row
    except pyodbc.DatabaseError as e:
        print(f"{datetime.now()}:ERROR - Cannot find address - {e}")
        return row
    finally:
        #Close connections if they still exist
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    
#Screen for just choosing the client)
def clientchoose():
    server = 'SQL-SSRS'
    database = 'Appz'
    try:
        # Connect to DB and fetch client data
        cnxn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes')
        cursor = cnxn.cursor()
        query = "SELECT clid, descr FROM clid WHERE descr IS NOT NULL"
        cursor.execute(query)

        # Create mappings
        descr_to_clid = {}
        descr_list = []
        for row in cursor.fetchall():
            clid, descr = row
            descr_to_clid[descr] = clid
            descr_list.append(descr)
            selected_value = {"value": None}

        #GUI actions
        def on_ok():
            selected_descr = combo.get()
            selected_value["value"] = descr_to_clid.get(selected_descr)
            main_window.destroy()

        def on_selection(event):
            ok_button.config(state="normal")
        #If you press an alphabetical key, dropdown menu will skip to the next client starting with that letter. Tab will also select the current client highlighted (activating ok button)
        def on_keypress(event):
            letter = event.char.lower()
            if event.keysym == "Tab" and combo.current() != -1:
                on_selection()
                return
            elif not letter.isalpha():
                return
            current_index = combo.current()
            total_items = len(descr_list)
            for i in range(1, total_items + 1):
                next_index = (current_index + i) % total_items
                if descr_list[next_index].lower().startswith(letter):
                    combo.current(next_index)
                    break
        main_window = tk.Tk()
        main_window.title("Choose Client")
        main_window.geometry("350x150")
        #dropdown menu initialised with client list
        text_label = tk.Label(main_window,text = "No address on some rows.\nPlease choose a client to pull an address from.")
        text_label.pack(pady=5)
        combo = ttk.Combobox(main_window, state="readonly", values=descr_list)
        combo.place(x=50, y=40)
        combo.bind("<<ComboboxSelected>>", on_selection)
        combo.bind("<Key>", on_keypress)
        #ok button initialised disabled until a client is selected
        ok_button = tk.Button(main_window, text="OK", state="disabled", command=on_ok)
        ok_button.place(x=130, y=100)

        main_window.wait_window()

        return selected_value["value"]
        
    except Exception as e:
        print(f"Error: {e}")
    return