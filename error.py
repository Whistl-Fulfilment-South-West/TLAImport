import pandas as pd
import os
import re
from datetime import datetime

def errorchex(df):
    #Double make sure ERROR column is initialised
    if "ERROR" not in df.columns:
        df["ERROR"] = ""

    
    #Concatenate Address columns if they exist and the single ADDRESS column does not
    # Rename if necessary
    if "ADDRESS" in df and "ADDRESS2" in df:
        df = df.rename(columns={"ADDRESS": "ADDRESS1"})

    if "DELADDRESS" in df and "DELADDRESS2" in df:
        df = df.rename(columns={"DELADDRESS": "DELADDRESS1"})

    # Concatenate Address and Delivery Address
    if "ADDRESS" not in df:
        df = concatenate_columns(df, "ADDRESS")

    if "DELADDRESS" not in df:
        df = concatenate_columns(df, "DELADDRESS")
    
   
    #List required columns
    required_columns = ["REF_NO", "PART", "QTY", "FIRSTNAME", "SURNAME", "ADDRESS", "CITY", "POSTCODE"]
    
    #confirm required columns exist in dataframe
    for col in required_columns:
    #if not, add error.
        if col not in df.columns:
            add_error(df, f"{col} column does not exist")
    
    #if any errors at this point, return to main - NO ROW CHECKS IF COLUMNS MISSING
    if df["ERROR"].any():
        return df
    
    #Perform checks on individual rows
    df = df.apply(rowchex, axis = 1)
    df = df.apply(error_none, axis = 1)
    
    #Make sure part is not a float, and remove trailing ".0" if it is
    df["PART"] = df["PART"].apply(lambda x: str(int(x)) if isinstance(x, float) and pd.notna(x) else str(x))
    
    return df

def rowchex(row):
    required_columns = ["REF_NO", "PART", "QTY", "FIRSTNAME", "SURNAME", "ADDRESS", "CITY", "POSTCODE"]
    errors = []

    for col in required_columns:
        if row[col] == "" or pd.isna(row[col]):
            errors.append(f"{col} column empty")

    #Order number length check
    if len(str(row["REF_NO"])) > 12:
        errors.append("Ref_No too long (>12 chars)")

    # Order total numeric check
    if "ORDTOTAL" in row.index and not pd.isna(row["ORDTOTAL"]):
        try:
            row["ORDTOTAL"] = float(row["ORDTOTAL"])  # Try direct conversion first
        except (ValueError, TypeError):
            row["ORDTOTAL"] = re.sub(r'[^0-9.]', '', str(row["ORDTOTAL"]))
            if pd.isna(pd.to_numeric(row["ORDTOTAL"], errors='coerce')):
                errors.append("Order Total not a number")
            else:
                row["ORDTOTAL"] = float(row["ORDTOTAL"])

    # Unit price numeric check
    if "UNITPRICE" in row.index and not pd.isna(row["UNITPRICE"]):
        try:
            row["UNITPRICE"] = float(row["UNITPRICE"])
        except (ValueError, TypeError):
            row["UNITPRICE"] = re.sub(r'[^0-9.]', '', str(row["UNITPRICE"]))
            if pd.isna(pd.to_numeric(row["UNITPRICE"], errors='coerce')):
                errors.append("Unit Price not a number")
            else:
                row["UNITPRICE"] = float(row["UNITPRICE"])
    # Delivery charge numeric check


    if "DELCHG" in row.index and not pd.isna(row["DELCHG"]):  # Use `.at`
        try:
            row["DELCHG"] = float(row["DELCHG"])
        except (ValueError, TypeError):
            row["DELCHG"] = re.sub(r'[^0-9.]', '', str(row["DELCHG"]))
            if pd.isna(pd.to_numeric(row["DELCHG"], errors='coerce')):
                errors.append("Postage Charge not a number")
            else:
                row["DELCHG"] = float(row["DELCHG"])
    #Qty numeric check
    if pd.isna(pd.to_numeric(row["QTY"], errors='coerce')):
        errors.append("Qty not a number or blank")
    else:
        row["QTY"] = float(re.sub(r'[^0-9.]','',str(round(row["QTY"]))))
        
    #Concat the errors into the error column using | as the join.
    
    if errors:
        row["ERROR"] = row["ERROR"] + "|" + "|".join(errors) if row["ERROR"] else "|".join(errors)

    
    return row

def add_error(df, err):
    df["ERROR"] = df["ERROR"].apply(lambda x: x + "|" + err if x else err)

def row_add_error(row,err):
    row["ERROR"] = row["ERROR"] + "|" + err if row["ERROR"] else err

def error_export(df,path,file,suffix = ".csv"):
    ind = file.find(suffix)
    errname = file[:ind] + "error" + file[ind:]
    errpath = path + "/errors"
    os.makedirs(errpath,exist_ok=True)
    df.to_csv(errpath + "/" + errname,index = False, header = True)

def error_none(row):
    if row["ERROR"] == "":
        row["ERROR"] = None
    return row

def concatenate_columns(df, prefix):
    cols = [f"{prefix}{i}" for i in range(1, 5) if f"{prefix}{i}" in df]
    if cols:
        print(f"{datetime.now()}: Concatenating {len(cols)} {prefix} Columns")
        df[prefix] = df[cols].fillna('').agg('~'.join, axis=1).str.replace(r"~+", "~", regex=True).str.strip("~")
    return df


def renames(df):
    df.rename(columns=lambda x: x[3:] if x.startswith("INV") else x, inplace=True)
    renam = {"ORDERNUMBER":"REF_NO","SKU":"PART","POSTAGE":"DELCHG","PAYMETH":"PAYMETHOD","PAYAMOUNT":"ORDTOTAL"}
    df.rename(columns=renam, inplace=True)
    df.rename(columns=lambda x: x.strip(), inplace = True)
    return df
