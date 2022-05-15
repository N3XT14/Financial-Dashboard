import camelot
from pathlib import Path

filename = Path("../BankStatement.pdf")
print(filename)
tables2=camelot.read_pdf('../BankStatement.pdf', flavor='stream', pages='1')
tables1=camelot.read_pdf(
    '../foo.pdf',
    password=None,
    flavor='lattice',
    suppress_stdout=False,
    layout_kwargs={}    
)
print(tables2)
print(type(tables2[0]))
print(tables2[1].df.head(2).to_dict())
print(tables2[1].df.iloc[:2].to_dict())
# for table in tables1:
#     #print(table.parsing_report)
#     reportObj = table.parsing_report
#     #print(reportObj['whitespace'])
#     if reportObj and reportObj["whitespace"] < 50:
#         print(table.df.iloc[1].to_list())
print(tables1[0])
print(tables1[0].parsing_report)