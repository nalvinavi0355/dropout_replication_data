import openpyxl, csv, sys
src,dst=sys.argv[1],sys.argv[2]
wb=openpyxl.load_workbook(src,read_only=True)
ws=wb.worksheets[0]
with open(dst,'w',newline='') as f:
    w=csv.writer(f)
    for r in ws.iter_rows(values_only=True): w.writerow(r)
print('done',src)
