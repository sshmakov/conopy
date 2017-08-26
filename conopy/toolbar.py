#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
import importlib

class ToolBar(QToolBar):
    def __init__(self, parent=None):
        super(ToolBar, self).__init__(parent)
        ini = QSettings("tools.ini", QSettings.IniFormat)
        ini.setIniCodec("utf-8")
        ini.beginGroup("Tools")
        for key in sorted(ini.childKeys()):
            v = ini.value(key)
            title = v[0]
            params = v[1:]
            a = self.addAction(title)
            a.params = params
            a.triggered.connect(self.execAction)
        ini.endGroup()
        #a = self.addAction("Excel")
        #a.triggered.connect(self.exportToExcel)

    def execAction(self):
        try:
            params = self.sender().params
            module = importlib.import_module(params[0])
            if len(params) < 2: func = "run()"
            else: func = params[1]
            exec("module."+func)
        except:
            print(str(sys.exc_info()[1]))
        return

    def exportToExcel(self):
        win = self.focusTaskWindow()
        if win == None:
            return
        view = self.focusItemView(win)
        title = win.windowTitle() + '.xlsx'
        if view == None:
            return

        # Create a workbook and add a worksheet.
        fileName = QFileDialog.getSaveFileName(self, 'Save Excel file', title,'Excel files (*.xlsx)')
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
                v = i.data()
                if isinstance(v, QDateTime):
                    if v.isValid() and v.toPyDateTime() > datetime.datetime(1900,1,1):
                        v = v.toPyDateTime()
                        worksheet.write_datetime(i.row() - minRow+1, i.column() - minCol, v, date)
                        continue
                    else:
                        v = v.toString(dateFormat)
                worksheet.write(i.row() - minRow+1, i.column() - minCol, v)

            workbook.close()
        except:
            QMessageBox.critical(self,'Export error',str(sys.exc_info()[1]))
            return
        

    def focusTaskWindow(self):
        try:
            return QApplication.instance().focusedTaskWindow()
        except:
            return None

    def focusItemView(self, win):
        if win == None: return None
        w = win.focusWidget()
        if w != None and isinstance(w, QTableView):
            return w
        views = win.findChildren(QTableView)
        if type(views) == type([]) and len(views)>0:
            return views[0]
        return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ToolBar()
    flags = Qt.Tool | Qt.WindowDoesNotAcceptFocus # | ex.windowFlags()
    ex.setWindowFlags(flags)
    ex.show()
    sys.exit(app.exec_())
