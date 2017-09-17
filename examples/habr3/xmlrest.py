#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtXmlPatterns import *
import meshandler


class XmlRestExecutor(QWidget):
    def __init__(self, iniFile, parent=None):
        super().__init__(parent)
        
        self.topLay = QVBoxLayout(self)
        self.topLay.setContentsMargins(6,6,6,6)
        self.lay = QFormLayout()
        self.topLay.addLayout(self.lay)
        self.resultLay = QVBoxLayout()
        self.topLay.addLayout(self.resultLay)
        
        self.man = QNetworkAccessManager(self)
        
        self.page = QWebEngineView(self)
        self.page.settings().setDefaultTextEncoding("windows-1251")
        self.topLay.addWidget(self.page)
        self.bar = QStatusBar(self)
        self.topLay.addWidget(self.bar)
        self.loadIni(iniFile)
##        self.man.finished.connect(self.netFinished)

    def loadIni(self, iniFile):
        ini = QSettings(iniFile, QSettings.IniFormat)
        ini.setIniCodec("utf-8")

        ini.beginGroup("Common")
        wt = ini.value('Title','')
        if wt != '': self.setWindowTitle(wt)
        ini.endGroup()

        ini.beginGroup("WebPage")
        self.url = ini.value('Url')
        self.bodyFile = ini.value('Body')
        self.method = ini.value('Method')
        if self.method == None:
            self.method = 'get' if self.bodyFile == None else 'post'
        self.transformTemplate = ini.value('Transform')
        ini.endGroup()

        self.readInputs(ini)

        self.runBtn = QPushButton("Run")
        self.runBtn.setDefault(True)
        self.runBtn.clicked.connect(self.run)
        self.btnLay = QHBoxLayout()
        self.btnLay.addStretch()
        self.btnLay.addWidget(self.runBtn)
        self.lay.addRow(self.btnLay)
        
    def readInputs(self, ini):
        self.inputs = {}
        self.params = []
        ini.beginGroup("Input")
        for key in sorted(ini.childKeys()):
            v = ini.value(key)
            if type(v) != type([]):
                v = [v]
            if len(v)>1:
                paramTitle = v[0]
                paramValue = v[1]
            else:
                paramTitle = key
                paramValue = v[0]
            self.params.append([key, paramTitle, paramValue])
            if paramTitle != '':
                le = QLineEdit()
                self.inputs[key] = le
                le.setText(paramValue)
                le.paramTitle = paramTitle
                self.lay.addRow(paramTitle, le)
        for kp in self.params:
            key = kp[0]
            paramTitle = kp[1]
            paramValue = kp[2]
            if paramTitle == '':
                le = self.inputs[paramValue]
                self.inputs[key] = le
        ini.endGroup()

    def run(self):
        self.runBtn.setEnabled(False)
        try:
            values = { kp[0]:self.inputs[kp[0]].text() for kp in self.params}
            url = self.url.format(**values)
            req = QNetworkRequest(QUrl(url))
            if self.method == 'get':
                reply = self.man.get(req)
            else:
                f = QFile(self.bodyFile)
                if f.open(QIODevice.ReadOnly):
                    body = str(f.readAll(),'utf-8-sig')
                else:
                    body = ''
                body = body.format(**values)
                body = bytes(body,'utf-8')
                req.setHeader(QNetworkRequest.ContentTypeHeader,"text/xml;charset=UTF-8")
                reply = self.man.post(req,body)
            reply.finished.connect(self.replyFinished)
        except:
            self.runBtn.setEnabled(True)
            print(str(sys.exc_info()[1]))


    def replyFinished(self):
        self.runBtn.setEnabled(True)
        reply = self.sender()
        hasTempl = False
        if self.transformTemplate != None:
            filename, ext = os.path.splitext(self.transformTemplate)
            if ext.lower() == '.xq' or ext.lower() == '.xquery':
                lang = QXmlQuery.XQuery10
            elif  ext.lower() == '.xsl' or ext.lower() == '.xslt':
                lang = QXmlQuery.XSLT20
            else:
                return
            templ = QFile(self.transformTemplate)
            if templ.open(QIODevice.ReadOnly):
                hasTempl = True
            else:
                print("Can't open template",self.transformTemplate)
        if hasTempl:
            query = QXmlQuery(lang)
            query.setMessageHandler(XmlQueryMessageHandler())
            query.setFocus(reply)
            query.setQuery(templ)
            if query.isValid():
                out = query.evaluateToString()
                if out != None:
                    self.page.setHtml(out)
                    return
        if reply.error() != QNetworkReply.NoError:
            print("Error:", reply.error())
            return
        b = reply.readAll()
        cth = reply.header(QNetworkRequest.ContentTypeHeader)
        if len(cth.split(';')) == 1:
            cth = cth + ";charset=windows-1251"
        self.page.setContent(b,cth,reply.url())
        return

class XmlQueryMessageHandler(QAbstractMessageHandler):
    def handleMessage(self, msgType, desc, idUrl, source):
        print("Msg(%s) on (%s,%s): %s" % (msgType, source.line(), source.column(), desc))

if __name__ == '__main__':
# Download OpenGL dll from here
# http://download.qt.io/development_releases/prebuilt/llvmpipe/windows/
#
#    os.environ.putenv('QT_OPENGL','software') # desktop, software, angle
    app = QApplication(sys.argv)
    ex = XmlRestExecutor("valcurs.ini")
    ex.show()
    sys.exit(app.exec_())


    

    
