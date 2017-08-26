#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import xlsxwriter

def exportToExcel():
    win = focusTaskWindow()
    if win == None:
        print("No focused window")
        return
    view = focusItemView(win)
    title = win.windowTitle() + '.xlsx'
    if view == None:
        print("No focused item view")
        return

    # Create a workbook and add a worksheet.
    fileName = QFileDialog.getSaveFileName(None, 'Save Excel file', title,'Excel files (*.xlsx)')
    if fileName == ('',''): return

    indexes = view.selectedIndexes()
    if len(indexes) == 0:
        indexes = view.selectAll()
        indexes = view.selectedIndexes()
    model = view.model()
    print(model)
    minRow = None
    minCol = None
    headers = dict()
    for i in indexes:
        if minRow == None: minRow = i.row()
        if minCol == None: minCol = i.column()
        minRow = min(minRow, i.row())
        minCol = min(minCol, i.column())
        if not i.column() in headers:
            headers[i.column()] = model.headerData(i.column(), Qt.Horizontal)

    try:
        workbook = xlsxwriter.Workbook(fileName[0])
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})
        dateFormat = 'dd.MM.yyyy'
        date = workbook.add_format({'num_format': dateFormat})

        for col in headers:
            worksheet.write(0, col - minCol, headers[col], bold)
        
        for i in indexes:
            try:
                v = i.data()
                if isinstance(v, QDateTime):
                    if v.isValid() and v.toPyDateTime() > datetime.datetime(1900,1,1):
                        v = v.toPyDateTime()
                        worksheet.write_datetime(i.row() - minRow+1, i.column() - minCol, v, date)
                        continue
                    else:
                        v = v.toString(dateFormat)
                worksheet.write(i.row() - minRow+1, i.column() - minCol, v)
            except:
                print(str(sys.exc_info()[1]))

        workbook.close()
    except:
        QMessageBox.critical(None,'Export error',str(sys.exc_info()[1]))
        return
    

def focusTaskWindow():
    try:
        return QApplication.instance().focusedTaskWindow()
    except:
        print(str(sys.exc_info()[1]))
        return None

def focusItemView(win):
    if win == None: return None
    w = win.focusWidget()
    if w != None and isinstance(w, QTableView):
        return w
    views = win.findChildren(QTableView)
    if type(views) == type([]) and len(views)>0:
        return views[0]
    return None

