#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import xlsxwriter
import conopy.util as util

class LinksMenu(QMenu):
   sections = None
   win = None
   view = None
   def __init__(self, win, parent=None):
      super().__init__(parent)
      self.win = win
      if not win:
         #print("No focused window")
         return
      self.view = util.focusItemView(self.win)
      if not self.view:
         #print("No focused item view")
         return
      index = self.view.currentIndex()
      if not index.isValid():
         return
      self.row = index.row()
      model = self.view.model()
      #self.headers = [ str(model.headerData(col, Qt.Horizontal)).upper() for col in range(model.columnCount()) ]
      self.headers = []
      for col in range(model.columnCount()):
         d = model.headerData(col, Qt.Horizontal, Qt.EditRole)
         if d is None:
            d = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
         self.headers.append(str(d).upper())
      self.roles = win.fieldRoles if 'fieldRoles' in dir(win) else {}  # { role: fieldName }
      self.roles = { str(r).upper():str(self.roles[r]).upper() for r in self.roles }
      #print('headers',self.headers)
      #print('roles',self.roles)
      iniFile = util.nearFile('.','data/links.ini')
      ini = QSettings(iniFile, QSettings.IniFormat)
      ini.setIniCodec("utf-8")
      ini.beginGroup('Links')
      self.sections = ini.value('Sections')
      ini.endGroup()
      if self.sections is None:
         return
      if type(self.sections) != type([]):
         self.sections = [self.sections]
      #print(self.sections)
      rhset = set(self.headers).union(set(self.roles))
      for s in self.sections:
         ini.beginGroup(s)
         t = ini.value('Title')
         if not t:
            t = s
         params = ini.value("Params")
         if params is None:
            params = []
         if type(params) != type([]):
            params = [params]
         exeIni = ini.value("Ini")
         ini.endGroup()
         upar = [ p.upper()  for p in params]
         #print('sect',s,'params',upar)
         if not set(upar).issubset(rhset):
            #print('not added')
            continue
         a = self.addAction(t)
         a.params = params
         a.exeIni = util.nearFile(iniFile,exeIni)
         a.iniFile = iniFile
         a.section = s
         a.win = win
         #print('added')
      self.triggered.connect(self.exeAction)

   def isValid(self):
      return self.win and self.view and self.sections

   def exeAction(self, a):
      model = self.view.model()
      #print(2, a.params, a.exeIni)
      values = {}
      for p in a.params:
         par = str(p).upper()
         if not par in self.headers:
            if par in self.roles:
               par = self.roles[par]
         try:
            col = self.headers.index(par)
            values[p] = model.index(self.row, col).data(Qt.DisplayRole)
         except:
            #print(str(sys.exc_info()[1]))
            #print(a.params)
            return

      #print(3, values)
      w = util.mainWindow.runIni(a.exeIni)
      w.clearParamValues()
      for v in values:
         w.setParamValue(v, values[v])   
   

def showMenu(win):
   menu = LinksMenu(win)
   if menu.isValid():
      menu.exec(QCursor.pos())
