#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtQuickWidgets import *
from PyQt5.QtQuick import *

import PyQt5
import os
if __package__ is None or __package__ == '':
    import util
else:
    from . import (util)

class QmlWin(QQuickWidget):
    def __init__(self, iniFile, parent=None):
        super().__init__(parent)
        self.statusChanged = self.showStatus
        self.setMinimumSize(QSize(100,100))
        self.setResizeMode(self.SizeRootObjectToView)
        pyqt = os.path.dirname(PyQt5.__file__)
        p = os.path.join(pyqt, "Qt", "qml")
        self.engine().addImportPath(p)
        ini = QSettings(iniFile, QSettings.IniFormat)
        ini.setIniCodec("utf-8")
        ini.beginGroup("QML")
        self.qml = ini.value("Source")
        if not self.qml is None:
            self.qml = QUrl.fromUserInput(util.nearFile(iniFile, self.qml))
            self.setSource(QUrl(self.qml))
        else:
            print("No source qml")

    def showStatus(status):
        print(status)
    
    
if __name__ == '__main__':
    import meshandler
    import sys

    os.environ.putenv('QT_ANGLE_PLATFORM','warp') # d3d11, d3d9 and warp
    os.environ.putenv('QT_OPENGL','software') # desktop, software, angle
    pyqt = os.path.dirname(PyQt5.__file__)
    QApplication.addLibraryPath(os.path.join(pyqt, "Qt", "plugins"))

    app = QApplication(sys.argv)
    w = QmlWin("../data/kanban/kanban.ini")
    w.show()
    sys.exit(app.exec_())
