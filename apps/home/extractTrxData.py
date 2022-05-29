import camelot
import re
from pathlib import Path
from datetime import date, datetime as dt
from itertools import groupby
import pandas as pd
import json

f = open ('apps/static/assets/json/banks.json', "r")
bankStructure = json.loads(f.read())

# re_num = '\d*[\,\d*].?\d+'
re_num = '^\d\d*[,]?\d*[,]?\d*[.,]?\d*\d+'

def convert(s, dformat):    
    return dt.strptime(s, dformat)

def kotakSpecial(l1, headerMap):    
    length = len(l1[2:])
    debit = ["0.00(Dr)"]*length
    credit = ["0.00(Cr)"]*length
    i,start = 2,0
    while(i != length):        
        if l1[i].endswith("Dr)"):
            debit[start] = l1[i]
        else:
            credit[start] = l1[i]
        i+=1
        start+=1
    headerMap['Debit'] = debit
    headerMap['Credit'] = credit    


def createDataStores(data, bankName):
    headerMap = {}
    for index, ele in enumerate(data):
        if bankName == 'kotak':
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
        
        if col_list[0] == 'Withdrawal (Dr)/':
            kotakSpecial(col_list, headerMap)
        elif col_list[0] not in headerMap:
            headerMap[col_list[0]] = col_list[1:]
        else:
            headerMap[col_list[0]].extend(col_list[1:])
    
    return headerMap

dateMap = {
    "Total_Amount": 0,
    "Total_Debit": 0,
    "Total_Credit": 0
}
def mapDateWithDataStore(headerMap, bankName):
    format = [bankStructure[bankName]["dateFormat"]]*len(headerMap["Date"])
    dateList = list(map(convert, headerMap["Date"], format))    
    balance = headerMap['Balance']
    debit = headerMap['Debit']
    credit = headerMap['Credit']
    for index,i in enumerate(dateList):        
        k = str(i.month) + " " + str(i.year)
        bal = float(re.findall(re_num, balance[index])[0].replace(',',''))
        creditVal = float(re.findall(re_num, credit[index])[0].replace(',',''))
        debitVal = float(re.findall(re_num, debit[index])[0].replace(',',''))
        if k not in dateMap:
            dateMap[k] = {}            
            dateMap[k]['Debit'] = [debitVal]
            dateMap[k]['Credit'] = [creditVal]
        else:
            dateMap[k]['Debit'].append(debitVal)
            dateMap[k]['Credit'].append(creditVal)
        dateMap[k]['Balance'] = bal
        dateMap['Total_Credit'] += creditVal
        dateMap['Total_Debit'] += debitVal
    dateMap['Total_Amount'] = bal

    return

def createResponseObj(result):    
    resObj = {
        'Total Amount': dateMap['Total_Amount'],
        'Total Debit': dateMap['Total_Debit'],
        'Total Credit': dateMap['Total_Credit']
    }
    print(resObj)
    return resObj


def extractData(fileList, bankName):
    for file in fileList:
        # file[1].save(Path.home() / file[0])        
        # filename = Path.home() / file[0]        
        # filename = str(filename).replace("\\","/")
        
        tables2=camelot.read_pdf("D:/ME/Projects/Python/BankStatement.pdf", flavor=bankStructure[bankName]["type"], pages='all')
        #print(tables2)
        for table in tables2:
            reportObj = table.parsing_report
            if reportObj and reportObj["whitespace"] < 50:         
                df_data = table.df
                #print(df_data)
                headerMap = createDataStores(df_data, bankName)
                mapDateWithDataStore(headerMap, bankName)
        resObj = createResponseObj(dateMap)
        # print(dateMap)
    return resObj
# extractData(['BankStatement.pdf'], 'kotak')
# filename = Path("D:/ME/Projects/Python/BankStatement.pdf").absolute()
# print(filename)
# filename = str(filename).replace("\\","/")
# tables2=camelot.read_pdf("../../BankStatement.pdf", flavor='stream', pages='1')
# tables2=camelot.read_pdf("D:/ME/Projects/Python/BankStatement.pdf", flavor='stream', pages='1')
# tables2=camelot.read_pdf(filename, flavor='stream', pages='1')
# tables1=camelot.read_pdf(
#     '../foo.pdf',
#     password=None,
#     flavor='lattice',
#     suppress_stdout=False,
#     layout_kwargs={}    
# )
# print(tables2[1].df)
# print(type(tables2[0]))
# print(tables2[1].df.head(2).to_dict())
# print(tables2[1].df.iloc[:2].to_dict())
# # for table in tables1:
# #     #print(table.parsing_report)
# #     reportObj = table.parsing_report
# #     #print(reportObj['whitespace'])
# #     if reportObj and reportObj["whitespace"] < 50:
# #         print(table.df.iloc[1].to_list())
# print(tables1[0])
# print(tables1[0].parsing_report)