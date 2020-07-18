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
            if not any(row := [str(j).strip() if j is not None else "" for j in row]):
                break
            rows.append(row)
    return rows
