#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import xlsxwriter
import conopy.util as util

class ob():
   def test(self):
      return 1

def exportToExcel(win):
   if win == None:
      print("No focused window")
      return
   view = util.focusItemView(win)
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
   d = sortedIndexes(indexes)
   headers = { col:model.headerData(col, Qt.Horizontal) for col in d.columns }
   minRow = min(d.rows)
   minCol = min(d.columns)   

   try:
      workbook = xlsxwriter.Workbook(fileName[0])
      worksheet = workbook.add_worksheet()
      bold = workbook.add_format({'bold': True})
      dateFormat = 'dd.MM.yyyy'
      date = workbook.add_format({'num_format': dateFormat})
      realCol = 0
      for col in d.columns:
         worksheet.write(0, realCol, headers[col], bold)
         realRow = 1
         for row in d.rows:
            if (row, col) in d.indexes:
               try:
                  v = d.indexes[(row,col)].data(Qt.EditRole)
                  if isinstance(v, QDateTime):
                     if v.isValid() and v.toPyDateTime() > datetime.datetime(1900,1,1):
                        v = v.toPyDateTime()
                        worksheet.write_datetime(realRow, realCol, v, date)
                     else:
                        v = v.toString(dateFormat)
                        worksheet.write(realRow, realCol, v)
                  else:
                     worksheet.write(realRow, realCol, v)
               except:
                  print(str(sys.exc_info()[1]))
            realRow += 1
         realCol += 1
      workbook.close()
   except:
      QMessageBox.critical(None,'Export error',str(sys.exc_info()[1]))
      return

def copyAsHtml(win):
   def valueStr(v):
      if isinstance(v, QDateTime):
        return v.toString("dd.MM.yyyy HH:mm:ss")
      if isinstance(v, QDate):
        return v.toString("dd.MM.yyyy")
      if isinstance(v, QTime):
        return v.toString("HH:mm:ss")
      return str(v)
   if win == None:
      #print("No focused window")
      return
   view = util.focusItemView(win)
   if view == None:
      #print("No focused item view")
      return
   indexes = view.selectedIndexes()
   if len(indexes) == 0:
      indexes = view.selectAll()
      indexes = view.selectedIndexes()
   if len(indexes) == 0:
      return;
   model = view.model()
   try:
      d = sortedIndexes(indexes)
      text = ''
      html = '<table><tbody>\n'
      headers = { col:model.headerData(col, Qt.Horizontal) for col in d.columns }
      html += '<tr>'
      for c in d.columns:
         html += '<th>%s</th>' % headers[c]
      text += ','.join([headers[c] for c in d.columns]) + '\n'
      html += '</tr>\n' 
      for r in d.rows:
         html += '<tr>' 
         nextV = False
         for c in d.columns:
            if nextV:
               text += ','
            else:
               nextV = True
            if (r, c) in d.indexes:
               v = d.indexes[(r,c)].data(Qt.DisplayRole)
               html += '<td>%s</td>' % valueStr(v)
               text += valueStr(v)
            else:
               html += '<td></td>'
         html += '</tr>'
         text += '\n'
      html += '</tbody></table>'
      mime = QMimeData()
      mime.setHtml(html)
      mime.setText(text)
      clipboard = QApplication.clipboard()
      clipboard.setMimeData(mime)
   except:
      QMessageBox.critical(None,'Export error',str(sys.exc_info()[1]))

def sortedIndexes(indexes):
    d = ob()
    d.indexes = { (i.row(), i.column()):i for i in indexes }
    d.rows = sorted(list(set([ i[0] for i in d.indexes ])))
    d.columns = sorted(list(set([ i[1] for i in d.indexes ])))
    return d

