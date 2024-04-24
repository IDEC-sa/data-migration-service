import re
import pandas as pd
import django.core.exceptions as excep
from .models import QuoteRequest, Product, ProductLine, ProductList, Company
from django.db import transaction
from django.core import exceptions
### whatsapp ###
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import os
from django.conf import settings
from django.utils import timezone

######
def convert_ranged(start_r, num_rows, columns_list, df):
    end_r = start_r + num_rows
    finDf1 = df.iloc[start_r:end_r, columns_list:].reset_index(drop=True)
    cols = [re.sub('[\W]', '', str(x)).lower() for x in list(finDf1.iloc[0].str.strip())]
    finDf1.columns = cols
    finDf1.head()
    return finDf1.drop(axis = 1, index = 0)

def convert_xlsx(excel):
    prods = validate_prods(excel)
    finProds = prods.loc[:, [ (str(col).strip().lower() != "nan") for col in prods.columns]]
    # finProds.drop(["image"], axis = 1, inplace=True)
    prds_only = finProds[:finProds["lineitem"].str.contains("nan").argmin()]
    # req_prods = prds_only[prds_only["totalpricesar"].str.strip() != "Option"]
    # prds_only.loc[:, "internalcode"] = prds_only.loc[:, "internalcode"].str.strip()
    return prds_only

def validate_prods(excel):
    df = pd.read_excel(excel, header=None)
    print(df.head())
    requiredd_cols = ["lineitem", "qty", "unitprice", "totalprice", "internalcode"]
    start = df.iloc[:, 0] == "start"    
    print(start.any())    
    if start.sum() == 0 and not start.any():
        raise excep.ValidationError("please specify the products table with the start key word")

    to_start = (df.iloc[:, 0] == "start").argmax() + 1
    prods = convert_ranged(to_start, 70, 0, df)
    cols = set(prods.columns[:])
    cols = [str(col).replace("\n", " ").strip().lower()  if isinstance(col, str) else col for col in cols]
    errors = []
    print(cols)
    for col in requiredd_cols:
        if col not in cols:
            errors.append({col:f"column {col} should exist"})
    if errors:
        raise excep.ValidationError(errors)
    return prods

@transaction.atomic
def createProdsFromQuoteRequest(quoteReqeust:QuoteRequest):
    errors = []
    df = convert_xlsx(quoteReqeust.excel)
    print(df)
    prods = df.to_dict('records')
    prodList = ProductList(quoteRequest=quoteReqeust)
    prodLines = []
    try:
        with transaction.atomic():
            prodList.save()
            for prod in prods:
                print(f"count = {len(prodLines)}")
                actualInternalProd = Product.objects.get(internalCode=prod["internalcode"])
                productLine = ProductLine(product = actualInternalProd, lineItem = prod["lineitem"], 
                                        quantity=prod["qty"], unitPrice=prod["unitprice"])
                
                if re.match(str(prod["totalprice"]).lower().strip(), r"option"):
                    productLine.optional = True
                productLine.productList = prodList
                print("before clean")
                try:
                    productLine.full_clean()
                except exceptions.ValidationError as e:
                    for k, v in e.message_dict.items():
                        errors.append(f"The following errors happened in field {k}: {''.join(v)} of product number {len(prodLines) + 1}.")
                print("after clean")
                prodLines.append(productLine)
            ProductLine.objects.bulk_create(prodLines)
            quoteReqeust.productsAdded = True
            quoteReqeust.save()
    except exceptions.ObjectDoesNotExist as e:
        errors.append(f"product in line number {len(prodLines) + 1} and internal code {prod['internalcode']} doesn't exist in the database. please check your internal code thouroghly or contact with the admin")
    except Exception as e:
            errors.append(f"error happened.")
    return errors

def validate(quoteReq:QuoteRequest):
    if quoteReq.state != "quo":
        raise excep.BadRequest("The requested quote can't be validated")
    else:
        quoteReq.state = "val"
    quoteReq.save()

def draften(quoteReq:QuoteRequest):
    if quoteReq.state == "quo" or quoteReq.state == "val":
        quoteReq.state = "dra"
        quoteReq.save()
    else:
        raise excep.BadRequest("The requested quote can't me marked as draft")


def create_prods(excel):
    productsDf = pd.read_excel(excel)
    productsDf.loc[:, "internalCode"][productsDf["internalCode"].isna()] = "notSpecified"
    prdouctsDict = productsDf.to_dict('records')
    print(prdouctsDict)
    errors = []
    prods = []
    try:
        for prod in prdouctsDict:
            with transaction.atomic():
                newProd = Product(**prod)
                prods.append(newProd)
        Product.objects.bulk_create(prods)
    except Exception as e:
        if prod:
            errors.append(f"error {e} happened during the creation process of product number {prod['internalCode']}")
        else:
            errors.append(f"error {e} happened")

    return errors

def create_comps(excel):
    compsDf = pd.read_excel(excel)
    compsDf.loc[:, "code"][compsDf["code"].isna()] = "notSpecified"
    compsDf = compsDf.to_dict('records')
    print(compsDf)
    errors = []
    comps = []
    try:
        for com in compsDf:
            with transaction.atomic():
                newCom = Company(**com)
                comps.append(newCom)
        Company.objects.bulk_create(comps)
    except Exception as e:
        if com:
            errors.append(f"error {e} happened during the creation process of product number {com['internalCode']}")
        else:
            errors.append(f"error {e} happened")
    return errors

def generateCsv(quote:QuoteRequest):
    
    opt = ProductLine.objects.filter(productList__quoteRequest=quote, optional=True)
    mand = ProductLine.objects.filter(productList__quoteRequest=quote, optional=False)
    optDict = {"sale_order_option_ids/product_id/id":[],
            "sale_order_option_ids/quantity": [],
            "sale_order_option_ids/price_unit":[],
            "Optional Products Lines/Display Name":[]}
    mandDict = {
        "order_line/product_uom_qty":[],
        "order_line/price_unit":[],
        "order_line/product_id/id":[]
               }

    for prodLine in mand:
        mandDict["order_line/product_uom_qty"].append(prodLine.quantity)
        mandDict["order_line/price_unit"].append(prodLine.unitPrice)
        mandDict["order_line/product_id/id"].append(prodLine.product.odooRef)

    for prodLine in opt:
        optDict["sale_order_option_ids/product_id/id"].append(prodLine.product.odooRef)
        optDict["sale_order_option_ids/quantity"].append(prodLine.quantity)
        optDict["sale_order_option_ids/price_unit"].append(prodLine.unitPrice)
        optDict["Optional Products Lines/Display Name"].append(prodLine.product.name)

    optDf = pd.DataFrame(optDict, index = [num for num in range(len(opt))])
    mandDf = pd.DataFrame(mandDict, index = [num for num in range(len(mand))])
    statics = {
        "id":quote.id,
        "quote_description":quote.static_data.projectName,
        "estimate_date":quote.static_data.date,
        "date_order":quote.static_data.date,
        "user_id/id": "__export__.res_users_57_a38dd07d",
        "reviewer_ids/id":"__export__.res_users_45_3f77bb43",
        "approver_id/id":"__export__.res_users_45_3f77bb43",
        "rfq_number":quote.static_data.quotationReference,
        "partner_id/id":quote.company.code
    }
    df = pd.DataFrame(statics, index = [0])
    finDdf = pd.concat([df, optDf, mandDf])
    finDdf.to_csv("finalCsv2.csv")



def sendWhatsappReport(message):
    my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    options = Options()
    #put the profile data in docker volume
    options.add_argument(f"user-data-dir={str(os.getcwd())}/chromedir")
    options.add_argument("--headless")
    prefs = {"download.default_directory": "."}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f"--user-agent={my_user_agent}")
    browser = webdriver.Chrome( options=options)
    name = "trial g"
    BASE_URL = "https://web.whatsapp.com/"

    browser.get(BASE_URL)
    print("Kindly go to output tab and login before the timeout of 120 seconds.")
    driver_ua = browser.execute_script("return navigator.userAgent")
    print("User agent:")
    print(driver_ua)
    try:
        wait = WebDriverWait(browser, 30)  # Adjust the timeout value as needed (e.g., 60 seconds)
        wait.until(EC.presence_of_element_located((By.XPATH, f"//span[./text()='{name}']")))
        sxpath = browser.find_element("xpath", f"//span[./text()='{name}']")
        action = webdriver.common.action_chains.ActionChains(browser)
        action.move_to_element_with_offset(sxpath, 0, 0)
        action.click()
        action.perform()
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div/p')))
        inp_xpath = ('//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div/p')
        input_box = WebDriverWait(browser, 60).until(expected_conditions.presence_of_element_located((By.XPATH, inp_xpath)))
        input_box.send_keys(message)
        input_box.send_keys(Keys.ENTER)
        time.sleep(10)
        
    except Exception as e:
        print(e)
        print("The above error happened while sending the message")
    finally:
        browser.quit()


def toMessage(filters, query):
    msg = [f"This is a generated report of the odoo data migration service created at {timezone.now().date()}"]
    for filter_n, filter_v in filters.items():
        msg.append(f"{filter_n}:  {filter_v}")
    
    for result in query:
        msg.append(f"Salesman email: {result['email']}: Number of created quotations: {result['total']}")
    return msg
