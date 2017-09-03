#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import PyQt5
import os


class WebWin(QWebEngineView):
    def __init__(self, iniFile, parent=None):
        super(WebWin, self).__init__(parent)
        ini = QSettings(iniFile, QSettings.IniFormat)
        ini.setIniCodec("utf-8")
        ini.beginGroup("Web")
        baseUrl = ini.value("BaseURL")
        if baseUrl != None:
            baseUrl = QUrl(baseUrl)
        else:
            baseUrl = QUrl()
        html = ini.value("Source")
        url = ini.value("URL")
        if html != None:
            f = QFile(html)
            f.open(QIODevice.ReadOnly)
            self.setContent(f.readAll())
        else:
            if url != None:
                self.setUrl(QUrl(url))
            
    
    
if __name__ == '__main__':
    import meshandler
    import sys

    pyqt = os.path.dirname(PyQt5.__file__)
    print(QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    os.environ['QT5DIR'] = os.path.join(pyqt, "Qt")
    os.environ['QTWEBENGINEPROCESS_PATH'] = os.path.join(pyqt, "Qt", "bin", "QtWebEngineProcess.exe")
    QApplication.addLibraryPath(os.path.join(pyqt, "Qt", "plugins"))

    app = QApplication(sys.argv)
    w = WebWin("../examples/webbrowser/2048.ini")
    w.show()
    sys.exit(app.exec_())
