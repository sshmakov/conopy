#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import importlib

class ToolBar(QToolBar):
    def __init__(self, iniFile, parent=None):
        super(ToolBar, self).__init__(parent)
        ini = QSettings(iniFile, QSettings.IniFormat)
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
    ex = ToolBar("tools.ini")
    flags = Qt.Tool | Qt.WindowDoesNotAcceptFocus # | ex.windowFlags()
    ex.setWindowFlags(flags)
    ex.show()
    sys.exit(app.exec_())
