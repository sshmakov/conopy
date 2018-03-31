#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
if __package__ is None or __package__ == '':
    from executor import PyExecutor
    import meshandler, dbpool, util
else:
    from . import (meshandler, dbpool, util)
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
        self.view = None
        self.proxyEnabled = True
        self.createFilterPane()
        

    def createFilterPane(self):
        self.filterLay = QHBoxLayout()
        self.btnLay.insertLayout(0,self.filterLay)
        self.fieldChoice = QComboBox(self)
        self.filterLay.addWidget(self.fieldChoice)
##        self.fieldOp = QComboBox(self)
##        self.filterLay.addWidget(self.fieldOp)
        self.valueFind = QComboBox(self)
        self.valueFind.setEditable(True)
        self.valueFind.setMinimumWidth(200)
        self.filterLay.addWidget(self.valueFind)
        self.btnFilter = QPushButton('Filter',self)
        self.btnFilter.setCheckable(True)
        self.btnFilter.clicked.connect(self.filterClick)
        self.filterLay.addWidget(self.btnFilter)
        self.resetFieldChoice()
        

    def loadIni(self, iniFile):
        self.columnHeaders = {}
        super().loadIni(iniFile);
        ini = QSettings(iniFile, QSettings.IniFormat)
        ini.setIniCodec('utf-8')

        ini.beginGroup("DB")
        self.dbini = ini.value("DBConnect")
        if self.dbini == "this":
           self.dbini = iniFile
        self.dbini = util.nearFile(self.iniFile, self.dbini)
        ini.endGroup()

        ini.beginGroup("Run")
        if ini.contains("SQL"):
            self.sql = ini.value("SQL")
        else:
            scriptFile = ini.value("SQLScript")
            scriptFile = util.nearFile(self.iniFile, scriptFile)
            # print("scriptFile:", scriptFile)
            f = QFile(scriptFile)
            f.open(QIODevice.ReadOnly)
            self.sql = str(f.readAll(),'utf-8-sig')
        #print(bytes(self.sql,'utf-8'))
        ini.endGroup()
        ini.beginGroup("Columns")
        for key in ini.childKeys():
            self.columnHeaders[key.strip().upper()] = ini.value(key)
        ini.endGroup()
        

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

    def showResult(self):
        super().showResult()
        err = self.query.lastError()
        if err.type() != QSqlError.NoError:
            self.bar.showMessage("Error {0} {1}".format(
                err.number(), err.text()))
            return
        res = self.query.result()
        while res and self.query.isSelect():
            self.createViewModel()
            self.view.sqlModel.setQuery(self.query)
            self.query.first()
            self.renameHeaders(self.view.sqlModel)
            if not self.query.nextResult():
                break
            res = self.query.result()
            
        self.bar.showMessage(
            "Rows affected: {0}  Rows: {1}".format(
                self.query.numRowsAffected(), self.query.size() ))
        self.resetFieldChoice()

    def renameHeaders(self, model):
        #hv = view.horizontalHeader()
        #model = view.model()
        for i in range(model.columnCount()):
            name = model.headerData(i, Qt.Horizontal, Qt.DisplayRole)
            idx = name.strip().upper()
            if idx in self.columnHeaders:
                nn = self.columnHeaders[idx]
                model.setHeaderData(i, Qt.Horizontal, name, Qt.EditRole)
                model.setHeaderData(i, Qt.Horizontal, nn, Qt.DisplayRole)
                #ov = model.headerData(i, Qt.Horizontal, Qt.EditRole)
                #model.setHeaderData(i, Qt.Horizontal, nn, Qt.EditRole)
                #d = model.headerData(i, Qt.Horizontal, Qt.DisplayRole)
                #v = model.headerData(i, Qt.Horizontal, Qt.EditRole)
                #print(name,'/',ov,'-->',d,'/',v)

    def filterClick(self):
        if self.btnFilter.isChecked():
            self.view.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
            self.view.proxyModel.setFilterKeyColumn(self.fieldChoice.currentIndex()-1)
            self.view.proxyModel.setFilterRegExp(self.valueFind.currentText())
        else:
            self.view.proxyModel.setFilterRegExp("")

    def resetFieldChoice(self):
        cur = self.fieldChoice.currentText()
        self.fieldChoice.clear()
        self.fieldChoice.addItem("- Любое поле -")
        model = self.view.model() if self.view else None
        if model:
            headers = [str(model.headerData(c,Qt.Horizontal)) for c in range(self.view.model().columnCount())]
            self.fieldChoice.addItems(headers)
        self.fieldChoice.setCurrentText(cur)
        

    def createModel(self, parent=None):
##        if parent and parent.sqlModel:
##            return parent.sqlModel
        return QSqlQueryModel(parent)

    def createProxy(self, parent=None):
        if parent and parent.proxyModel:
            return parent.proxyModel
        proxy = QSortFilterProxyModel(parent)
        proxy.setDynamicSortFilter(True)
        proxy.setSortRole(Qt.EditRole)
        return proxy

    def clearResult(self):
        self.bar.clearMessage()

    def createViewModel(self):
        if not self.view:
            self.view = QTableView(self)
            vh = self.view.verticalHeader()
            vh.setDefaultSectionSize(19)
            self.view.setSortingEnabled(True)
            self.view.horizontalHeader().setSectionsMovable(True)
            self.view.horizontalHeader().setSortIndicator(-1,Qt.AscendingOrder)
            self.resultLay.addWidget(self.view)
            self.view.sqlModel = None
            self.view.proxyModel = None
        if not self.view.sqlModel:
            self.view.sqlModel = self.createModel(self.view)
        if self.proxyEnabled:
            if not self.view.proxyModel:
                self.view.proxyModel = self.createProxy(self.view)
            self.view.proxyModel.setSourceModel(self.view.sqlModel)
            self.view.setModel(self.view.proxyModel)
        else:
            self.view.setModel(self.view.sqlModel)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ini = util.nearFile(__file__,"../data/sqlite/test-sqlite.ini")
    ex = SqlExecutor(ini)
    ex.show()

    sys.exit(app.exec_())
