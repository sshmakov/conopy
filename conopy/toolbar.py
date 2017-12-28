#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, re
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import importlib

class ToolBar(QToolBar):
    def __init__(self, iniFile, parent=None):
        super(ToolBar, self).__init__(parent)
        ini = QSettings(iniFile, QSettings.IniFormat)
        ini.setIniCodec("utf-8")
        rx = re.compile('([^(]+)\s*(?:\((.*)\))?')
        ini.beginGroup("Tools")
        for key in sorted(ini.childKeys()):
            v = ini.value(key)
            title = saveTitle = v[0]
            params = v[1:]
            tkey = rx.findall(title)
            keySeq = None            
            if tkey and len(tkey) == 1 and len(tkey[0]) == 2 and len(tkey[0][1])>0:
                title = tkey[0][0].lstrip().rstrip()
                keySeq = QKeySequence(tkey[0][1])
            a = self.addAction(title)
            a.params = params
            a.triggered.connect(self.execAction)
            if keySeq:
                a.setShortcut(keySeq)
            a.setToolTip(saveTitle)
        ini.endGroup()

    def execAction(self):
        try:
            params = self.sender().params
            module = importlib.import_module(params[0])
            if len(params) < 2: func = "run(win)"
            else: func = params[1]
            win = self.focusTaskWindow()
            if func.find('(') < 0:
                exec("module.%s(win)" % func)
            else:
                exec("module.%s" % func)
        except:
            print(str(sys.exc_info()[1]))
        return

    def focusTaskWindow(self):
        try:
            return QApplication.instance().focusedTaskWindow()
        except:
            return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ToolBar("tools.ini")
    flags = Qt.Tool | Qt.WindowDoesNotAcceptFocus # | ex.windowFlags()
    ex.setWindowFlags(flags)
    ex.show()
    sys.exit(app.exec_())
