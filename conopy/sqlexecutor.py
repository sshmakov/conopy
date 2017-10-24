#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
if __package__ is None or __package__ == '':
    from executor import PyExecutor
    import meshandler
    import dbpool
else:
    from . import (meshandler, dbpool)
    from .executor import PyExecutor

class QueryRunner(QThread):
    def __init__(self, query, parent=None):
        super(QueryRunner, self).__init__(parent)
        self.query = query
        return
    
    def run(self):
        self.query.exec_()


class SqlExecutor(PyExecutor):
    def __init__(self, iniFile, parent=None):
        super().__init__(iniFile, parent)

    def loadIni(self, iniFile):
        super().loadIni(iniFile);
        ini = QSettings(iniFile, QSettings.IniFormat)

        ini.beginGroup("DB")
        self.dbini = ini.value("DBConnect")
        if self.dbini == "this":
           self.dbini = iniFile
        self.dbini = os.path.join(
            os.path.split(
                os.path.abspath(self.iniFile))[0], self.dbini)
        ini.endGroup()

        ini.beginGroup("Run")
        if ini.contains("SQL"):
            self.sql = ini.value("SQL")
        else:
            scriptFile = ini.value("SQLScript")
            scriptFile = os.path.join(os.path.split(
                os.path.abspath(self.iniFile))[0], scriptFile)
            print("scriptFile:", scriptFile)
            f = QFile(scriptFile)
            f.open(QIODevice.ReadOnly)
            self.sql = str(f.readAll(),'utf-8-sig')
        #print(bytes(self.sql,'utf-8'))
        ini.endGroup()
        

    def createModel(self, parent=None):
        return QSqlQueryModel(parent)

    def showResult(self):
        super().showResult()
        err = self.query.lastError()
        if err.type() != QSqlError.NoError:
            self.bar.showMessage("Error {0} {1}".format(
                err.number(), err.text()))
        else:
            self.bar.showMessage(
                "Rows affected: {0}  Rows: {1}".format(
                    self.query.numRowsAffected(), self.query.size() ))
            res = self.query.result()
            while res and self.query.isSelect():
                w = self.createView()
                w.sqlModel = self.createModel(w)
                w.sqlModel.setQuery(self.query)
                self.query.first()
                w.proxyModel = QSortFilterProxyModel(w)
                w.proxyModel.setSourceModel(w.sqlModel)
                w.setModel(w.proxyModel)
                self.resultLay.addWidget(w)
                if not self.query.nextResult():
                    break
                res = self.query.result()

    def run(self):
        self.runBtn.setEnabled(False)
        self.clearResult()
        
        self.db = dbpool.openDatabase(self.dbini)
        if self.db == None or not self.db.isValid() or not self.db.isOpen():
            print("No opened DB", self.dbini)
            self.endRun()
            return
        if self.sql != "":
            self.query = QSqlQuery(self.db)
            self.query.setNumericalPrecisionPolicy(QSql.HighPrecision)
            self.query.prepare(self.sql)
            pi = 0
            for p in self.params:
                key = p[0]
                if key in self.inputs:
                    le = self.inputs[key]
                    par = ':'+key
                    self.query.bindValue(par, le.text())
                    pi = pi + 1
            self.tr = QueryRunner(self.query)
            self.tr.finished.connect(self.showResult)
            self.tr.start();

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SqlExecutor("../data/test-sqlite.ini")
    ex.show()

    sys.exit(app.exec_())
