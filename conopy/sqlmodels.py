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
        if not parent.isValid():
            return len(self.records)
        return 0

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.columns)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role in (Qt.DisplayRole, Qt.EditRole):
            r = index.row(); c = index.column()
            if r < 0 or r >= len(self.records):
                return None
            row = self.records[r]                                   
            if c < 0 or c >= len(self.columns):
                return None
            #return row[c]['value']
            v = row[c]['value']
            if role == Qt.DisplayRole:
                if isinstance(v, QDateTime):
                    return v.toString("dd.MM.yyyy HH:mm:ss")
                if isinstance(v, QDate):
                    return v.toString("dd.MM.yyyy")
                if isinstance(v, QTime):
                    return v.toString("HH:mm:ss")
                return str(v)
            return v
        return None

    def headerData(self, index, orient, role=Qt.DisplayRole):
        if role in (Qt.DisplayRole, Qt.EditRole):
            if orient == Qt.Horizontal:
                if index < 0 or index >= len(self.columns):
                    return None
                return self.columns[index]['name']
            else:
                return index
        return None

    def index(self, row, column, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()
        return self.createIndex(row, column)

    def setQuery(self, query):
        self.beginResetModel()
        self.clearBuf()
        self.query = query
        rec = self.query.record()
        self.columns = [ {'name': rec.fieldName(c)}
                         for c in range(rec.count()) ]
        while self.query.next():
            rec = self.query.record()
            self.records.append( [ {'value': rec.value(c)}
                                   for c in range(rec.count()) ])
        self.endResetModel()

    def parent(self, index):
        return QModelIndex()

    def clearBuf(self):
        self.records = []
        self.columns = []
        

if __name__ == '__main__':
    import meshandler
    import dbpool
    app = QCoreApplication(sys.argv)
    m = MSSQLModel()
    db = dbpool.openDatabase('../data/sqlite/sqlite.ini')
    sql = QSqlQuery("SELECT * FROM ACCOUNTS", db)
    sql.exec_()
    m.setQuery(sql)
    print('rowCount',m.rowCount())
    print('columnCount',m.columnCount())
    print('display data',m.index(0,0).data(Qt.DisplayRole))
    print('edit data',m.index(0,0).data(Qt.EditRole))
    print('headerData',m.headerData(0,Qt.Horizontal))
    
    
    
