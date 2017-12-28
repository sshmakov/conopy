#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

mainWindow = None

def nearFile(baseFile, path):
    if not path:
        return path
    if not baseFile or baseFile == '.':
        baseFile = mainWindow.dataPath if mainWindow else './dummy'
    return os.path.abspath(os.path.join(os.path.split(os.path.abspath(baseFile))[0], path))

def focusItemView(win):
    if win == None: return None
    w = win.focusWidget()
    if w != None and isinstance(w, QTableView):
        return w
    views = win.findChildren(QTableView)
    if type(views) == type([]) and len(views)>0:
        return views[0]
    return None

def headerNames(model, minCol, maxCol):
    headers = dict()
    for col in range(minCol, maxCol+1):
        headers[col] = model.headerData(col, Qt.Horizontal)
    return headers

