""" Module containing helper functions for the robot """

import tempfile

from datetime import date

from pathlib import Path

import win32com.client as win32


def export_excel_to_pdf(binary_excel: bytes, pdf_path: str):
    """
    Docstring for export_excel_to_pdf

    :param binary_excel: Description
    :type binary_excel: bytes
    :param pdf_path: Description
    :type pdf_path: str
    """

    Path(pdf_path).parent.mkdir(parents=True, exist_ok=True)

    # 1. Write the Excel file to a temp location
    temp_xlsx = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx").name
    with open(temp_xlsx, "wb") as f:
        f.write(binary_excel)

    # 2. Use Excel COM automation
    excel = win32.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    wb = excel.Workbooks.Open(temp_xlsx)
    ws = wb.Worksheets(1)

    # ---- Print settings (MATCHES YOUR SCREENSHOT) ----

    # Paper size A3
    xlPaperA3 = 8
    ws.PageSetup.PaperSize = xlPaperA3

    # Landscape
    ws.PageSetup.Orientation = 2  # xlLandscape

    # Fit to 1 page
    ws.PageSetup.Zoom = False
    ws.PageSetup.FitToPagesWide = 1
    ws.PageSetup.FitToPagesTall = 1

    # Normal margins
    ws.PageSetup.LeftMargin = excel.InchesToPoints(0.7)
    ws.PageSetup.RightMargin = excel.InchesToPoints(0.7)
    ws.PageSetup.TopMargin = excel.InchesToPoints(0.75)
    ws.PageSetup.BottomMargin = excel.InchesToPoints(0.75)

    # No gridlines etc (optional)
    ws.PageSetup.PrintGridlines = False
    ws.PageSetup.PrintHeadings = False

    # ----------------------------------------------------

    # 3. Export to PDF
    wb.ExportAsFixedFormat(0, pdf_path)

    wb.Close(SaveChanges=False)
    excel.Quit()


def get_current_quarter():
    """
    Helper func to retrieve the current quarter
    """

    today = date.today()
    year = today.year
    month = today.month

    if 1 <= month <= 3:
        current_quarter = "Q1"

    elif 4 <= month <= 6:
        current_quarter = "Q2"

    elif 7 <= month <= 9:
        current_quarter = "Q3"

    else:
        current_quarter = "Q4"

    return f"{year}{current_quarter}", today


def get_next_quarter():
    """
    Helper func to retrieve next quarter as 'YYYYQx'
    """

    today = date.today()
    year = today.year
    month = today.month

    if 1 <= month <= 3:
        next_quarter = "Q2"

    elif 4 <= month <= 6:
        next_quarter = "Q3"

    elif 7 <= month <= 9:
        next_quarter = "Q4"

    else:
        # Currently Q4 → next is Q1 next year
        next_quarter = "Q1"
        year += 1

    return f"{year}{next_quarter}"
