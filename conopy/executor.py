#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
if __package__ is None or __package__ == '':
    import dbpool
    import meshandler
else:
    from . import (dbpool, meshandler)

class PyExecutor(QWidget):
    focused = pyqtSignal()
    
    def __init__(self, iniFile, parent=None):
        super().__init__(parent)
        self.iniFile = iniFile
        self.setWindowTitle(QFileInfo(iniFile).baseName())
        self.setWindowFlags(self.windowFlags()
                            | Qt.WindowMinimizeButtonHint
                            | Qt.WindowMaximizeButtonHint
                            )
        self.topLay = QVBoxLayout(self)
        self.topLay.setContentsMargins(6,6,6,6)
        self.lay = QFormLayout()
        self.topLay.addLayout(self.lay)
        self.resultLay = QVBoxLayout()
        self.topLay.addLayout(self.resultLay)
        self.bar = QStatusBar(self)
        self.topLay.addWidget(self.bar)
        
        self.loadIni(iniFile)

    def loadIni(self, iniFile):
        #print("Ini", iniFile, "loading")
        ini = QSettings(iniFile, QSettings.IniFormat)
        ini.setIniCodec("utf-8")
        self.inputs = {}
        self.params = []
        ini.beginGroup("Common")
        wt = ini.value('Title','')
        if wt != '': self.setWindowTitle(wt)
        ini.endGroup()
        self.readInputs(ini)
        self.readFieldRoles(ini)

        self.runBtn = QPushButton("Run")
        self.runBtn.setDefault(True)
        self.runBtn.clicked.connect(self.run)
        self.btnLay = QHBoxLayout()
        self.btnLay.addStretch()
        self.btnLay.addWidget(self.runBtn)
        self.lay.addRow(self.btnLay)

    def readInputs(self, ini):
        ini.beginGroup("Input")
        for key in sorted(ini.childKeys()):
            v = ini.value(key).split(':')
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

    def readFieldRoles(self, ini):
        roles = {}
        ini.beginGroup("FieldRoles")
        for key in ini.childKeys():
            roles[key] = ini.value(key)
        ini.endGroup()
        self.fieldRoles = roles

    def clearParamValues(self):
        for paramName in self.inputs:
            le = self.inputs[paramName]
            le.setText('')

    def setParamValue(self,paramName, value):
        if paramName in self.inputs:
            le = self.inputs[paramName]
            le.setText(str(value))
        else:
            print('Not found param name', paramName)

    def focusInEvent(self,event):
        super().focusInEvent(event)
        self.focused.emit()

    def createView(self):
        view = QTableView(self)
        vh = view.verticalHeader()
        vh.setDefaultSectionSize(19)
        view.setSortingEnabled(True)
        view.horizontalHeader().setSectionsMovable(True)
        view.horizontalHeader().setSortIndicator(-1,Qt.AscendingOrder)
        return view

    def clearResult(self):
        self.bar.clearMessage()
        while (self.resultLay.count() > 0 ):
            child = self.resultLay.takeAt(0)
            w = child.widget()
            if not w is None: w.deleteLater()

    def showResult(self):
        self.endRun()

    def endRun(self):
        self.runBtn.setEnabled(True)
        
    def run(self):
        self.runBtn.setEnabled(False)
        self.clearResult()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PyExecutor("test-sqlite.ini")
    ex.show()

    sys.exit(app.exec_())
