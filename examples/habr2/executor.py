#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
import meshandler
from dbpool import *

class QueryRunner(QThread):
    def __init__(self, query, parent=None):
        super(QueryRunner, self).__init__(parent)
        self.query = query
        return
    
    def run(self):
        self.query.exec_()


class PyExecutor(QDialog):
    focused = pyqtSignal()
    
    def __init__(self, iniFile, parent=None):
        super(PyExecutor, self).__init__(parent)
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
        ini = QSettings(iniFile, QSettings.IniFormat)
        ini.setIniCodec("utf-8")
        self.inputs = {}
        self.params = []
        ini.beginGroup("Common")
        wt = ini.value('Title','')
        if wt != '': self.setWindowTitle(wt)
        ini.endGroup()
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

        ini.beginGroup("DB")
        self.dbini = ini.value("DBConnect")
        if self.dbini == "this":
           self.dbini = iniFile
        ini.endGroup()

        ini.beginGroup("Run")
        if ini.contains("SQL"):
            self.sql = ini.value("SQL")
        else:
            f = QFile(ini.value("SQLScript"))
            f.open(QIODevice.ReadOnly)
            self.sql = str(f.readAll(),'utf-8-sig')
        #print(bytes(self.sql,'utf-8'))
        ini.endGroup()
        
        self.runBtn = QPushButton("Run")
        self.runBtn.setDefault(True)
        self.runBtn.clicked.connect(self.run)
        self.btnLay = QHBoxLayout()
        self.btnLay.addStretch()
        self.btnLay.addWidget(self.runBtn)
        self.lay.addRow(self.btnLay)

    def focusInEvent(self,event):
        super(PyExecutor, self).focusInEvent(event)
        self.focused.emit()

    def createTableView(self):
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
            if w != None: w.deleteLater()

    def showQueryResult(self):
        err = self.query.lastError()
        if err.type() != QSqlError.NoError:
            self.bar.showMessage("Error {0} {1}".format(
                err.number(), err.text()))
        else:
            self.bar.showMessage(
                "Rows affected: {0}  Rows: {1}".format(
                    self.query.numRowsAffected(), self.query.size() ))
            res = self.query.result()
            while res and res.isSelect():
                w = self.createTableView()
                w.sqlModel = QSqlQueryModel(w)
                w.sqlModel.setQuery(self.query)
                self.query.first()
                w.proxyModel = QSortFilterProxyModel(w)
                w.proxyModel.setSourceModel(w.sqlModel)
                w.setModel(w.proxyModel)
                self.resultLay.addWidget(w)
                if not self.query.nextResult():
                    break
                res = self.query.result()
        self.endRun()

    def endRun(self):
        self.runBtn.setEnabled(True)
        
    def run(self):
        self.runBtn.setEnabled(False)
        self.clearResult()
        self.db = openDatabase(self.dbini)
        if self.db == None or not self.db.isValid() or not self.db.isOpen():
            print("No opened DB", self.dbini)
            self.endRun()
            return
        if self.sql != "":
            self.query = QSqlQuery(self.db)
            self.query.setNumericalPrecisionPolicy(QSql.HighPrecision)
            self.query.prepare(self.sql)
            for p in self.params:
                key = p[0]
                if key in self.inputs:
                    le = self.inputs[key]
                    par = ':'+key
                    self.query.bindValue(par, le.text())
            self.tr = QueryRunner(self.query)
            self.tr.finished.connect(self.showQueryResult)
            self.tr.start();

if __name__ == '__main__':
    import os
    import PyQt5
    import sys

    pyqt = os.path.dirname(PyQt5.__file__)
    QApplication.addLibraryPath(os.path.join(pyqt, "Qt", "plugins"))
    
    app = QApplication(sys.argv)
    ex = PyExecutor("artists.ini")

    ex.show()

    sys.exit(app.exec_())
