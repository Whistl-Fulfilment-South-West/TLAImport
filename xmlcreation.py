import pandas as pd
import xml.etree.cElementTree as ET
import datetime
import os

def xml_creation(o,df,dest):
    
    #Drop columns with no values in them
    df = df.dropna(axis = 1,how = 'all')

    #create variables for order details
    full_values = list(df.columns.values)

    #define the line values
    line_values = ["PART","QTY","UNITPRICE","PERSONALISATION"]

    #extract order values from the full values (ie not in line values)
    order_values = [v for v in full_values if v not in line_values]
    order_dict = {}
        
    #add order values to dictionary
    for val in order_values:
        order_dict[val] = df[val].iloc[0]

    #Drop columns with no values in them
    df = df.dropna(axis = 1,how = 'all')
    

    #Set the delivery address reference to either the order number or MAIN, depending on if the delivery address matches the invoice address.
    if "DELADDRESS" in order_dict and order_dict.get("DELADDRESS",order_dict["ADDRESS"]) != order_dict["ADDRESS"] and order_dict.get("DELADDRESS","") != "" and "ADDRREF" not in order_dict:
        delref = o
    else:
        delref = "MAIN"
    
    #Initialise order value variables
    otg = 0.0
    otn = 0.0
    otv = 0.0
    dcg = 0.0
    dcn = 0.0
    dcv = 0.0
    #Calculate delivery charge gross/tax/net
    if "DELCHG" in order_dict:
        dcg = order_dict["DELCHG"]
        dcn = round((dcg/6) * 5,2)
        dcv = round(dcg - dcn,2)

    #Calculate order total gross/tax/net
    if "ORDTOTAL" in order_dict:
        otg = order_dict["ORDTOTAL"]
        otn = round((otg/6) * 5,2)
        otv = round(otg - otn,2)
    elif "UNITPRICE" in full_values:
        df["LINETOTAL"] = df["UNITPRICE"] * df["QTY"]
        otg = df["LINETOTAL"].sum() + dcg
        otn = round((otg/6) * 5,2)
        otv = round(otg - otn,2)
    else:
        otg = dcg
        otn = round((otg/6) * 5,2)
        otv = round(otg - otn,2)

    #Convert all values in order_dict to strings. Helps serialisation when creating the XML at the end.
    order_dict = {k: str(v) for k, v in order_dict.items()}

    #XML Creation - order_dict has most of the order level values, others are in their own variables (set above).
    root = ET.Element("DTD_ORDER")
    head = ET.Element("OrderHead")
    root.append(head)
    ET.SubElement(head,"Site").text = order_dict.get("SITE","")
    ET.SubElement(head,"Method").text = order_dict.get("METHOD","")
    ET.SubElement(head,"OrderReferences").text = order_dict.get("REF_NO","")
    ET.SubElement(head,"Buyer").text = order_dict.get("CUSTOMER", "")
    ET.SubElement(head,"ExternalCustomerCode").text = order_dict.get("CUSTOMER", "")
    ET.SubElement(head,"OrderDate").text = order_dict.get("DATEREQUEST",datetime.datetime.now().strftime('%d/%m/%Y'))
    ET.SubElement(head,"CustType").text =  order_dict.get("CUSTTYPE", "")
    ET.SubElement(head,"OrderStatus").text =  order_dict.get("ORDERSTATUS", "30")
    if order_dict.get("ORDERSTATUS",30) == "210":
        ET.SubElement(head,"OrderHoldReason").text =  order_dict.get("HOLDREASON", "WEB")
    ET.SubElement(head,"CustomerReference").text =  order_dict.get("CUSTREF", "")
    ET.SubElement(head,"InvoiceInitials").text = order_dict.get("FIRSTNAME","")
    ET.SubElement(head,"InvoiceSurname").text = order_dict.get("SURNAME","")
    ET.SubElement(head,"InvoiceCompany").text = order_dict.get("COMPANY","")
    ET.SubElement(head,"InvoicePostcode").text = order_dict.get("POSTCODE","")
    ET.SubElement(head,"InvoiceAddress").text = order_dict.get("ADDRESS","")
    ET.SubElement(head,"InvoiceCity").text = order_dict.get("CITY","")
    ET.SubElement(head,"InvoiceCounty").text = order_dict.get("COUNTY","")
    ET.SubElement(head,"InvoiceCountry").text = order_dict.get("COUNTRY","GB")
    ET.SubElement(head,"InvoicePhone").text = order_dict.get("PHONE","")
    ET.SubElement(head,"InvoiceEmail").text = order_dict.get("EMAIL","")
    ET.SubElement(head,"OrdDelChrgGross").text = str(dcg)
    ET.SubElement(head,"OrdDelChrgNet").text = str(dcn)
    ET.SubElement(head,"OrdDelChrgTax").text = str(dcv)
    ET.SubElement(head,"OrdTotalGross").text = str(otg)
    ET.SubElement(head,"OrdTotalNet").text = str(otn)
    ET.SubElement(head,"OrdTotalTax").text = str(otv)
    ET.SubElement(head,"OrderSource").text = order_dict.get("SOURCE","WEB")
    ET.SubElement(head,"Currency").text = order_dict.get("CURRENCY","GBP")
    OptIn = ET.Element("OptInData")
    head.append(OptIn)
    ET.SubElement(OptIn,"Email").text = "F"
    ET.SubElement(OptIn,"Mail").text = "F"
    recip = ET.Element("OrderRecipient")
    head.append(recip)
    ET.SubElement(recip,"RecipientDelivery").text = "1"
    ET.SubElement(recip,"RecipientOrderType").text = ""
    ET.SubElement(recip,"RecipientAddressRef").text = order_dict.get("ADDRREF",delref)
    ET.SubElement(recip,"RecipientInitials").text = order_dict.get("DELFIRSTNAME",order_dict.get("FIRSTNAME",""))
    ET.SubElement(recip,"RecipientSurname").text = order_dict.get("DELSURNAME",order_dict.get("SURNAME",""))
    ET.SubElement(recip,"InvoiceCompany").text = order_dict.get("DELCOMPANY",order_dict.get("COMPANY",""))
    ET.SubElement(recip,"RecipientPostcode").text = order_dict.get("DELPOSTCODE",order_dict.get("POSTCODE",""))
    ET.SubElement(recip,"RecipientAddress").text = order_dict.get("DELADDRESS",order_dict.get("ADDRESS",""))
    ET.SubElement(recip,"RecipientCity").text = order_dict.get("DELCITY",order_dict.get("CITY",""))
    ET.SubElement(recip,"RecipientCounty").text = order_dict.get("DELCOUNTY",order_dict.get("COUNTY",""))
    ET.SubElement(recip,"RecipientCountry").text = order_dict.get("DELCOUNTRY",order_dict.get("COUNTRY","GB"))
    ET.SubElement(recip,"RecipientPhone").text = order_dict.get("DELPHONE",order_dict.get("PHONE",""))
    ET.SubElement(recip,"RecipientEmail").text = order_dict.get("DELEMAIL",order_dict.get("EMAIL",""))
    if "ORDERREQUEST" in order_dict:
        ET.SubElement(recip,"RecipientMessage").text = order_dict.get("ORDERREQUEST","")
    ET.SubElement(recip,"RecipientDelMessage").text = order_dict.get("DELMESS",'')
    ET.SubElement(recip,"RecipientDelChrgGross").text = str(dcg)
    ET.SubElement(recip,"RecipientDelChrgNet").text = str(dcn)
    ET.SubElement(recip,"RecipientDelChrgTax").text = str(dcv)
    ET.SubElement(recip,"RecipientCarrier").text = order_dict.get("CARRIER","RECALC")
    ET.SubElement(recip,"RecipientCarrierService").text = order_dict.get("DELMETHOD","RECALC")
    ET.SubElement(recip,"RecipientDespatchDate").text = ""
    ET.SubElement(recip,"RecipientCarrierFixed").text = "FIXED"
    line_number = 1 
    for _, row in df.iterrows():
        add_order_line(recip, row.to_dict(), line_number)
        line_number += 1
    pamt = ET.Element("OrderPayment")
    head.append(pamt)
    ET.SubElement(pamt,"CardType").text = order_dict.get("PAYMETHOD") or "WEB"
    ET.SubElement(pamt,"AuthMessage").text = ""
    ET.SubElement(pamt,"CardNumber").text = ""
    ET.SubElement(pamt,"AuthCode").text = ""
    ET.SubElement(pamt,"Amount").text = str(otg)
    tree = ET.ElementTree(root)
    try:
        with open(dest + "/" + o + ".xml","wb") as file:
            tree.write(file,encoding="utf-8",xml_declaration=True)
        return 0
    except Exception as e:
        print(f"{datetime.datetime.now()}: XML Creation Failed for order {o} - {e}")
        if os.path.exists(dest + "/" + o + ".xml"):
            os.remove(dest + "/" + o + ".xml")
        return 1
        

def add_order_line(parent, line_dict, line_number):
    #Generate XML for a single order line.

    line = ET.Element("OrderLine")
    parent.append(line)
    #Calculate line totals from unit price and quantity
    ltg = round(line_dict.get("UNITPRICE", 0) * line_dict.get("QTY", 1),2)
    ltn = round((ltg / 6) * 5,2)
    ltv = round(ltg - ltn,2)
    create_sub_element(line, "LineNumber", line_number)
    create_sub_element(line, "Product", line_dict.get("PART", ""))
    create_sub_element(line, "Quantity", line_dict.get("QTY", 1))
    create_sub_element(line, "Price", line_dict.get("UNITPRICE", 0))
    create_sub_element(line, "LineTotalGross", ltg)
    create_sub_element(line, "LineTotalNet", ltn)
    create_sub_element(line, "LineTotalTax", ltv)
    create_sub_element(line, "Personalised", line_dict.get("PERSONALISATION", ""))
    if "ORDERREQUEST" in line_dict:
        create_sub_element(line, "external_guid",line_dict.get("ORDERREQUEST",""))
    return line

def create_sub_element(parent, tag, text=""):
    elem = ET.SubElement(parent, tag)
    elem.text = str(text)
    return elem

    
    
    