import openpyxl
import xlrd


def xlsx_to_rows(filename, sheet=None):
    if filename.endswith(".xlsx"):
        wb = openpyxl.load_workbook(filename)
        if sheet:
            ws = wb[sheet]
        else:
            ws = wb.worksheets[0]
        rows = []
        for i in ws.rows:
            if not any(row := [str(j.value).strip() if j.value is not None else "" for j in i]):
                break
            rows.append(row)
    else:
        wb = xlrd.open_workbook(filename)
        if sheet:
            ws = wb.sheet_by_name(sheet)
        else:
            ws = wb.sheet_by_index(0)
        rows = []
        for i in range(ws.nrows):
            row = ws.row_values(i)
            types = list(ws.row_types(i))
            for index in range(len(row)):
                if types[index] == 3:
                    row[index] = xlrd.xldate_as_datetime(row[index], 0).strftime("%Y/%m/%d")
            if not any(row := [str(j).strip() if j is not None else "" for j in row]):
                break
            rows.append(row)
    return rows
