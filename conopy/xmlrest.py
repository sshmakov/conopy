#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
# Download OpenGL dll from here
# http://download.qt.io/development_releases/prebuilt/llvmpipe/windows/
#
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtXmlPatterns import *
if __package__ is None or __package__ == '':
    from executor import PyExecutor
    import meshandler, dbpool
    import util as cu
else:
    from . import (meshandler, dbpool)
    from .executor import PyExecutor
    from . import util as cu
from datetime import timedelta, datetime


class XmlRestExecutor(PyExecutor):
    def __init__(self, iniFile, parent=None):
        super().__init__(iniFile,parent)
        
        self.lastReply = None
        self.man = QNetworkAccessManager(self)
        #self.man.finished.connect(self.netFinished)
        self.man.sslErrors.connect(self.netSslErrors)
        self.man.authenticationRequired.connect(self.authenticationRequired)
        self.man.proxyAuthenticationRequired.connect(self.authenticationRequired)
        self.page = QWebEngineView(self)
        self.resultLay.addWidget(self.page)
        #self.loadIni(iniFile)
        self.startTime = datetime.now()
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.showTime)

    def loadIni(self, iniFile):
        super().loadIni(iniFile)
        ini = QSettings(iniFile, QSettings.IniFormat)
        ini.setIniCodec("utf-8")
        print(iniFile,ini.childGroups())
        ini.beginGroup("WebPage")
        self.url = ini.value('Url')
        self.bodyFile = ini.value('Body')
        self.method = ini.value('Method')
        if self.method is None:
            self.method = 'get' if self.bodyFile == None else 'post'
        if self.bodyFile:
            self.bodyFile = cu.nearFile(iniFile, self.bodyFile)

##        print(self.method)
        self.transformTemplate = ini.value('Transform')
        if self.transformTemplate:
            self.transformTemplate = cu.nearFile(iniFile, self.transformTemplate)
        ini.endGroup()

##        self.readInputs(ini)
##
##        self.runBtn = QPushButton("Run")
##        self.runBtn.setDefault(True)
##        self.runBtn.clicked.connect(self.run)
##        self.btnLay = QHBoxLayout()
##        self.btnLay.addStretch()
##        self.btnLay.addWidget(self.runBtn)
##        self.lay.addRow(self.btnLay)
        
    def readInputs(self, ini):
        self.inputs = {}
        self.params = []
        ini.beginGroup("Input")
        for key in sorted(ini.childKeys()):
            v = ini.value(key)
            print(v)
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

    def startedRun(self):
        self.runBtn.setEnabled(False)
        self.startTime = datetime.now()
        self.timer.start()
        self.showTime()
        
    def finishedRun(self):
        self.timer.stop()
        self.showTime()
        self.runBtn.setEnabled(True)
        self.lastReply = None

    def run(self):
        try:
            self.startedRun()
            values = { kp[0]:self.inputs[kp[0]].text() for kp in self.params}
##            print(values)
            url = self.url.format(**values)
##            print('url:',url)
            req = QNetworkRequest(QUrl(url))
##            print('method:',self.method)
            if self.method == 'get':
##                print("get", url)
                req.setHeader(QNetworkRequest.ContentTypeHeader,"text/xml;charset=UTF-8")
                req.setHeader(QNetworkRequest.ContentLengthHeader,"0")
##                req.setRawHeader("Accept","application/xhtml+xml")
##                print(req.rawHeaderList())
                reply = self.man.get(req)
            else:
                f = QFile(self.bodyFile)
                if f.open(QIODevice.ReadOnly):
                    body = str(f.readAll(),'utf-8-sig')
                else:
                    body = ''
                body = body.format(**values)
##                print('body:')
##                print(body)
##                print('----')
                body = bytes(body,'utf-8')
                req.setHeader(QNetworkRequest.ContentTypeHeader,"text/xml;charset=UTF-8")
##                print("post", url)
                reply = self.man.post(req,body)
            reply.finished.connect(self.replyFinished)
            reply.error.connect(self.replyError)
            #reply.sslErrors.connect(self.replySslErrors)
            reply.downloadProgress.connect(self.downloadProgress)
            err = reply.error()
            self.lastReply = reply
##            print("Error", err, reply.errorString())
##            print("Reply is running:", reply.isRunning())
##            print("Reply is finished:", reply.isFinished())
##            print("Reply man:", reply.manager())
##            print("Self man:", self.man)
            if err != QNetworkReply.NoError:
                self.finishedRun()
##            r = requests.get(self.url)
##            print(r.content)
        except:
            print(str(sys.exc_info()[1]))
            self.finishedRun()


    def replyFinished(self):
        self.netFinished(self.sender())
        
        
    def netFinished(self, reply):
        #reply = self.sender()
        #buf = reply.readAll()
##        print("finished")
        self.finishedRun()
        if reply is None:
##            print("reply is None")
            return
        if reply.isOpen():
            hasTempl = True
            if self.transformTemplate != None:
                filename, ext = os.path.splitext(self.transformTemplate)
    ##            print(filename, ext)
                if ext.lower() == '.xq' or ext.lower() == '.xquery':
                    lang = QXmlQuery.XQuery10
                elif  ext.lower() == '.xsl' or ext.lower() == '.xslt':
                    lang = QXmlQuery.XSLT20
                else:
                    return
                templ = QFile(self.transformTemplate)
                if not templ.open(QIODevice.ReadOnly):
                    print("Can't open template",self.transformTemplate)
                    hasTempl = False
            if hasTempl:
                query = QXmlQuery(lang)
                query.setMessageHandler(XmlQueryMessageHandler())
                query.setFocus(reply)
                query.setQuery(templ)
                if query.isValid():
                    out = query.evaluateToString()
    ##                print("out",out)
                    if out != None:
                        self.page.setHtml(out)
                        #self.finishedRun()
                        return
            b = reply.readAll()
        if reply.error() != QNetworkReply.NoError:
            print("Error:", reply.error())
        else:
            self.page.setContent(b,"text/plain;charset=windows-1251",reply.url())
        #self.finishedRun()
    
    def showTime(self):
        time = datetime.now()
        delta = time - self.startTime
        s = "In progress" if self.timer.isActive() else "Finished"
        self.bar.showMessage("%s. %s s" % (s, delta.seconds))
        if delta.seconds >= 30 and not (self.lastReply is None):
            self.lastReply.abort()

    def netSslErrors(self, reply, errors):
        print(errors)
        reply.ignoreSslErrors()

    def replySslErrors(self, errors):
        print(errors)
        self.netSslErrors(self.sender(), errors)

    def replyError(self, errorCode):
        reply = self.sender()
        print("Error", errorCode, reply.errorString())

    def authenticationRequired(self, reply, auth):
        print("authenticationRequired")

    def downloadProgress(self, received, total):
        print("progress %s/%s bytes" % (received, total))

class XmlQueryMessageHandler(QAbstractMessageHandler):
    def handleMessage(self, msgType, desc, idUrl, source):
        print("Msg(%s) on (%s,%s): %s" % (msgType, source.line(), source.column(), desc))

if __name__ == '__main__':
    os.environ.putenv('QT_ANGLE_PLATFORM','warp') # d3d11, d3d9 and warp
## warp:
##    ---------------------------
##QtWebEngineProcess.exe - Системная ошибка
##---------------------------
##Запуск программы невозможен, так как на компьютере отсутствует VCRUNTIME140.dll. Попробуйте переустановить программу. 
##---------------------------
##ОК   
##---------------------------

    os.environ.putenv('QT_OPENGL','software') # desktop, software, angle
#    os.environ.putenv('QT_OPENGL','angle') # desktop, software, angle
## software - нужно положить vcruntime140 в Qt/bin
    
    #os.environ.putenv('QT_D3DCOMPILER_DLL','C:/Windows/System32/D3DCompiler_47.dll')
    app = QApplication(sys.argv)
    ex = XmlRestExecutor("../data/ЦБ/valcurs.ini")
    ex.show()
    sys.exit(app.exec_())
