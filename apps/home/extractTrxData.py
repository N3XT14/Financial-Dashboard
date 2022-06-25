import imp
import camelot
import pikepdf
import re
from pathlib import Path
from datetime import date, datetime as dt
from itertools import groupby
import pandas as pd
import json
import sys
import traceback

f = open ('apps/static/assets/json/banks.json', "r")
bankStructure = json.loads(f.read())

# re_num = '\d*[\,\d*].?\d+'
re_num = '^\d\d*[,]?\d*[,]?\d*[.,]?\d*\d+'

def convert(s, dformat):
    return dt.strptime(s, dformat)

def sortRevByAmount(newL, index, top):    
    return sorted(newL, key = lambda newL:newL[index], reverse=True)[:top]

def calcPercentage(l, index, total, updateOriginal, roundUp):
    newL = []
    
    for itr, ele in enumerate(l):
        print(ele[index], total)     
        val = (ele[index]/total)*100
        newL.append(round(val))
        if updateOriginal:
            ele.append(round(val))
    return newL

def validateIfEmpty(record, cnt):  
    if record == [] or record == '':
        return float(0), cnt
    else:
        record = float(record[0].replace(',',''))
        return  record, cnt + 1 if record > 0 else cnt

def kotakSpecial(l1, headerMap):     
    length = len(l1)
    debit = ["0.00(Dr)"]*length
    credit = ["0.00(Cr)"]*length
    i = 0
    while(i != length):        
        if l1[i].endswith("Dr)"):
            debit[i] = l1[i]
        else:
            credit[i] = l1[i]
        i+=1
    headerMap['Debit'] = debit
    headerMap['Credit'] = credit

    return

def kotakSpecialDesc(l1, headerMap):
    description = []
    length,i = len(l1),0
    
    for i in range(0,length,2):
        if i+1 < length:
            description.append(l1[i] + l1[i+1])
    # while(i != length):
    #     i+=1    
    headerMap["Description"] = description

    return

def createDataStores(data, bankName):
    headerMap = {}
    for index, ele in enumerate(data):
        if bankName == 'kotak' and data[index][0] != 'Narration':
            col_list = list(filter(None, data[index]))
        else:
            col_list = list(data[index])        

        if col_list[0] in ['Txn Date','Transaction Date', 'Date']:
            col_list[0] = 'Date'
        if col_list[0] in ['Balance', 'Closing Balance']:
            col_list[0] = 'Balance'
        # if col_list[0] in ['Debit', 'Withdrawal', 'Withdraw']:
        #     col_list[0] = 'Debit'
        # if col_list[0] in ['Credit', 'Deposit']:
        #     col_list[0] = 'Credit'
        
        if col_list[0] == 'Withdrawal (Dr)/' and bankName == 'kotak':
            kotakSpecial(col_list[2:], headerMap)
        elif col_list[0] == 'Narration' and bankName == 'kotak':
            kotakSpecialDesc(col_list[1:], headerMap)                
        elif col_list[0] not in headerMap:            
            headerMap[col_list[0]] = list(map(lambda st: str.replace(st, "\n", " "), col_list[1:]))            
        else:
            headerMap[col_list[0]].extend(col_list[1:])
    # print(headerMap)
    return headerMap

def mapDateWithDataStore(dateMap, headerMap, bankName):
    format = [bankStructure[bankName]["dateFormat"]]*len(headerMap["Date"])
    dateList = list(map(convert, headerMap["Date"], format))    
    balance = headerMap["Balance"]
    debit = headerMap["Debit"]
    credit = headerMap["Credit"]
    desc = headerMap["Description"]
    creditCount, debitCount, totalTrx,j = 0, 0, 0,-1
    
    if len(desc) > len(dateList):
        desc = desc[1:]
    
    for index,i in enumerate(dateList):
        k = i.strftime("%b") + " " + str(i.year)
        bal, totalTrx = validateIfEmpty(re.findall(re_num, balance[index]), totalTrx)
        creditVal, creditCount = validateIfEmpty(re.findall(re_num, credit[index]), creditCount)
        debitVal, debitCount = validateIfEmpty(re.findall(re_num, debit[index]), debitCount)
        # print(f'Balance: {bal}, {creditCount}, CreditVal: {creditVal}, DebitVal: {debitVal}')
        if k not in dateMap:
            dateMap["Labels"][0].append(k)            
            dateMap[k] = {}            
            dateMap[k]["Debit"] = [debitVal]
            dateMap[k]["Credit"] = [creditVal]
            dateMap[k]["Debit_Sum"] = debitVal
            dateMap[k]["Credit_Sum"] = creditVal
            dateMap["Labels"][1].append(debitVal)
            dateMap["Labels"][2].append(creditVal)
            dateMap["Labels"][3].append(bal)
            j+=1
        else:
            dateMap[k]["Debit"].append(debitVal)
            dateMap[k]["Credit"].append(creditVal)
            dateMap[k]["Debit_Sum"] += debitVal
            dateMap[k]["Credit_Sum"] += creditVal
            dateMap["Labels"][1][j] += debitVal
            dateMap["Labels"][2][j] += creditVal
            dateMap["Labels"][3][j] = bal
        
        if debitVal != 0:            
            dateMap["Debit Trx List"].append([desc[index], str(i.day) + " " + k, debitVal])
        if creditVal != 0:
            dateMap["Credit Trx List"].append([desc[index], str(i.day) + " " + k, creditVal])
        dateMap[k]["Balance"] = bal
        dateMap["Total_Credit"] += creditVal
        dateMap["Total_Debit"] += debitVal
    # print(creditCount, debitCount)
    dateMap["Total_Amount"] = bal
    dateMap["Credit Count"] +=  creditCount
    dateMap["Debit Count"] += debitCount
    dateMap["Total Transaction"] += totalTrx

    return dateMap

def createResponseObj(result):
    calcPercentage(result["Debit Trx List"], 2, result["Total_Debit"], True, 0)
    calcPercentage(result["Credit Trx List"], 2, result["Total_Credit"], True, 0)

    resObj = {
        "Total Amount": result["Total_Amount"],
        "Total Transaction": result["Total Transaction"],
        "Total Credit": result["Total_Credit"],
        "Credit Count": result["Credit Count"],
        "Total Debit": result["Total_Debit"],
        "Debit Count": result["Debit Count"],
        "Date Response": result["Labels"],
        "Debit Trx List": sortRevByAmount(result["Debit Trx List"], 2, 10),
        "Credit Trx List": sortRevByAmount(result["Credit Trx List"], 2, 10)
    }    
    print("Result", resObj)
    return resObj


def extractData(fileList, bankName, password=''):
    for file in fileList:
        print(fileList, Path.home())
        file[1].save(Path.home() / file[0])
        filename = Path.home() / file[0]
        filename = str(filename).replace("\\","/")
        
        try :
            with pikepdf.Pdf.open(filename, password=password) as my_pdf:
                my_pdf.save(filename)
            tables2=camelot.read_pdf(filename, flavor=bankStructure[bankName]["type"], pages='all')
        except BaseException as ex:
            # Get current system exception
            print('Entered except')
            ex_type, ex_value, ex_traceback = sys.exc_info()

            # Extract unformatter stack traces as tuples
            trace_back = traceback.extract_tb(ex_traceback)

            # Format stacktrace
            stack_trace = list()

            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

            print("Exception type : %s " % ex_type.__name__)
            print("Exception message : %s" %ex_value)
            print("Stack trace : %s" %stack_trace)
        print(tables2)
        dateMap = {
            "Total_Amount": 0,
            "Total Transaction": 0,
            "Total_Credit": 0,
            "Credit Count": 0,
            "Total_Debit": 0,
            "Debit Count": 0,
            "Labels": [[] for i in range(4)],
            "Debit Trx List": [],
            "Credit Trx List": []
        }        
        for table in tables2:
            reportObj = table.parsing_report
            if reportObj and reportObj["whitespace"] < 50:         
                df_data = table.df
                # print(df_data)               
                headerMap = createDataStores(df_data, bankName)
                dateMap = mapDateWithDataStore(dateMap, headerMap, bankName)
        resObj = createResponseObj(dateMap)
        
    return resObj
