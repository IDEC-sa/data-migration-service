import re
import pandas as pd
import django.core.exceptions as excep
from .models import QuoteRequest, Product, ProductLine, ProductList, Company
from django.db import transaction
from django.core import exceptions

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
    prods = convert_ranged(to_start, 70, 1, df)
    cols = set(prods.columns[:])
    cols = [str(col).replace("\n", " ").strip().lower()  if isinstance(col, str) else col for col in cols]
    errors = []
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
                actualInternalProd = Product.objects.filter(internalCode=prod["internalcode"]).first()
                productLine = ProductLine(product = actualInternalProd, lineItem = prod["lineitem"], 
                                        quantity=prod["qty"], unitPrice=prod["unitprice"])
                if re.match(str(prod["totalprice"]).lower().strip(), r"option"):
                    productLine.optional = True
                productLine.productList = prodList
                prodLines.append(productLine)
            ProductLine.objects.bulk_create(prodLines)
            quoteReqeust.productsAdded = True
            quoteReqeust.save()
    except exceptions.ObjectDoesNotExist as e:
        errors.append(f"product in line number {prod['lineitem']} and internal code {prod['internalcode']} doesn't exist in the database. please check your internal code thouroghly or contact with the admin")
    except Exception as e:
        if prod:
            errors.append(f"error {e} happened during the creation process of product number {prod['internalcode']}.")
        else:
            errors.append(f"error {e} happened.")
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
      
