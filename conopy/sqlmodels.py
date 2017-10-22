#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import *
from PyQt5.QtSql import *

class MSSQLModel(QAbstractItemModel):
    def __init__(self, parent=None):
        self.query = None
        self.clearBuf()
        super().__init__(parent)

    def rowCount(self, parent=QModelIndex()):
        if self.query != None and self.query.isActive():
            return len(self.records)
        return 0

    def columnCount(self, parent=QModelIndex()):
        return len(self.columns)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and (role == Qt.DisplayRole
                                or role == Qt.EditRole):
            return self.records[index.row()][index.column()]['value']
        return None

    def headerData(self, index, orient, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orient == Qt.Horizontal:
                return self.columns[index]['name']
            else:
                return index
        return None

    def index(self, row, column, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()
        return self.createIndex(row, column)
##        return QModelIndex()

    def setQuery(self, query):
        self.clearBuf()
        self.query = query
        rec = self.query.record()
        self.columns = [ {'name': rec.fieldName(c)}
                         for c in range(rec.count()) ]
        while self.query.next():
            rec = self.query.record()
            self.records.append( [ {'value': rec.value(c)}
                                   for c in range(rec.count()) ])

    def parent(self, index):
        return QModelIndex()

    def clearBuf(self):
        self.records = []
        self.columns = []
        

if __name__ == '__main__':
    import meshandler
    import dbpool
    m = MSSQLModel()
    db = dbpool.openDatabase('../data/sqlite.ini')
    sql = QSqlQuery("SELECT * FROM ACCOUNTS", db)
    sql.exec_()
    m.setQuery(sql)
    print('rowCount',m.rowCount())
    print('columnCount',m.columnCount())
    print('data',m.index(0,0).data())
    print('headerData',m.headerData(0,Qt.Horizontal))
    
    
    
