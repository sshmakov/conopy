#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtQuickWidgets import *
import PyQt5
import os


class QmlWin(QQuickWidget):
    def __init__(self, iniFile, parent=None):
        super(QmlWin, self).__init__(parent)
        pyqt = os.path.dirname(PyQt5.__file__)
        p = os.path.join(pyqt, "Qt", "qml")
        self.engine().addImportPath(p)
        ini = QSettings(iniFile, QSettings.IniFormat)
        ini.setIniCodec("utf-8")
        ini.beginGroup("QML")
        qml = ini.value("Source")
        if qml != None:
            self.setSource(QUrl(qml))
        else:
            print("No source qml")
    
    
if __name__ == '__main__':
    import meshandler
    import sys

    pyqt = os.path.dirname(PyQt5.__file__)
    QApplication.addLibraryPath(os.path.join(pyqt, "Qt", "plugins"))

    app = QApplication(sys.argv)
    w = QmlWin("../dynamicview.ini")
    w.show()
    sys.exit(app.exec_())
