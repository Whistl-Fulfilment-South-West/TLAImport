import os
import time
from datetime import datetime, timedelta
import logging
import smtplib
from email.message import EmailMessage

def clear_archives(folders, days_old=30):
    now = time.time()
    cutoff = now - (days_old * 86400)

    for folder in folders:
        if not os.path.isdir(folder):
            logging.info(f"Skipping non-directory: {folder}")
            continue

        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    file_mtime = os.path.getmtime(file_path)

                    if file_mtime < cutoff:
                        try:
                            os.remove(file_path)
                            logging.info(f"Deleted: {file_path}")
                        except Exception as e:
                            logging.info(f"Error deleting {file_path}: {e}")



def check_import_folders_and_notify(folders, recipient_email, sender_email, smtp_server, smtp_port, sender_password):
    csv_found = []
    
    for folder in folders:
        if not os.path.isdir(folder):
            continue

        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith('.csv'):
                    csv_found.append(os.path.join(root, file))

    if csv_found:
        msg = EmailMessage()
        msg['Subject'] = 'CSV File Alert'
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.set_content("CSV files found in monitored folders:\n\n" + "\n".join(csv_found))

        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)
                logging.info("Alert email sent.")
        except Exception as e:
            logging.warning(f"Failed to send email: {e}")
    else:
        logging.info("No CSV files found. No email sent.")

def logclear(path, suffix = ".log"):
    for f in os.listdir(path):
        g = os.path.join(path, f)
        if g.endswith(suffix):
            if os.stat(g).st_mtime < time.time() - (30 * 86400):
                if os.path.isfile(g):
                    os.remove(g)


def main():
    log_dest = "C:/Development/python/xmlorderimport/TLACleanup/logs"
    os.makedirs(log_dest,exist_ok=True)

    #Setup logging - create log file
    logfile = f"{log_dest}/log{datetime.now().strftime("%Y%m%dT%H%M%S")}.log"
    open(logfile,"x")

    #Set logging parameters
    logging.basicConfig(filename=logfile,encoding = "utf-8", level = logging.DEBUG, style = '{', format="{asctime} - {levelname} - {message}",datefmt="%Y-%m-%d %H:%M",force = True)
    logging.info(f"Program started by {os.getenv("username")}")

    archive_folders = ["//Elucid9/elucid/Data_Import/Muddy/order_import/done","//Elucid9/elucid/Data_Import/Wrangaton_Multi/order_import/done","//Elucid9/elucid/Data_Import/Paignton_Multi/order_import/done"]
    logging.info(f"Beginning cleanup of archive folders")
    clear_archives(archive_folders)

    logging.info(f"Checking import folders for CSV files")
    import_folders = ["//Elucid9/elucid/Data_Import/Muddy/order_import","//Elucid9/elucid/Data_Import/Wrangaton_Multi/order_import","//Elucid9/elucid/Data_Import/Paignton_Multi/order_import"]
    check_import_folders_and_notify(import_folders,"isdg@cbfulfilment.co.uk","webfolders@whistl.co.uk")

    logging.info(f"Clearing old log files")
    logclear(log_dest)


if __name__ == "__main__":
    main()




