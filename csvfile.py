import pandas as pd
import os
import time
import glob
from datetime import datetime
from os import listdir
import chardet
import tkinter as tk
from tkinter import filedialog, messagebox
import sys

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

def archcleardown(source,suffix = ".csv"):
    arch = source + "/done"
    for f in os.listdir(arch):
        g = os.path.join(arch, f)
        if g.endswith(suffix):
            if os.stat(g).st_mtime < time.time() - (30 * 86400):
                if os.path.isfile(g):
                    os.remove(g)


def mess_display(message):
    def on_ok():
        message_window.destroy()

    message_window = tk.Tk()
    message_window.title("TLA Message")
    message_window.geometry("300x150")
    message_window.resizable(False, False)

    message = tk.Label(message_window, text=str(message), wraplength=280, justify="left", fg="black")
    message.pack(padx=10, pady=20)

    ok_button = tk.Button(message_window, text="OK", command=on_ok)
    ok_button.pack(pady=10)

    message_window.mainloop()

def dirsearch():
    

    def select_directory():
        directory = filedialog.askdirectory()
        if directory:
            selected_path.set(directory)

    def confirm_selection():
        directory = selected_path.get()
        if directory and os.path.isdir(directory):
            result["directory"] = directory
            root.destroy()
        else:
            messagebox.showerror("Invalid Directory", "The selected path is not a valid directory. Please choose another.")
    
    def exit_program():
        root.destroy()
        sys.exit()  # Forcefully exits the Python script

    # Create the GUI window
    root = tk.Tk()
    root.title("Select a Directory")
    root.geometry("500x180")

    selected_path = tk.StringVar()
    result = {"directory": None}

    # Handle the window close button
    root.protocol("WM_DELETE_WINDOW", exit_program)

    # Browse button
    tk.Button(root, text="Browse...", command=select_directory).pack(pady=10)

    # Display selected path
    tk.Label(root, textvariable=selected_path, wraplength=480, bg="white",
             relief="sunken", anchor="w", padx=5, pady=5).pack(fill="x", padx=10)

     # Button frame
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Confirm Selection", command=confirm_selection).pack(side="left", padx=10)
    tk.Button(button_frame, text="Exit", command=exit_program).pack(side="right", padx=10)

    # Run the GUI event loop (this blocks until root.destroy is called)
    root.mainloop()

    return result["directory"]
    
    
