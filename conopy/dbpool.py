#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *

class DBLoginDlg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lay = QFormLayout()
        self.setWindowTitle("Login to DB")
        self.topLay = QVBoxLayout(self)
        self.topLay.setContentsMargins(6,6,6,6)
        self.lay = QFormLayout()
        self.topLay.addLayout(self.lay)
        self.btnLay = QHBoxLayout()
        self.topLay.addLayout(self.btnLay)
        self.userEdit = QLineEdit(self)
        self.passEdit = QLineEdit(self)
        self.passEdit.setEchoMode(QLineEdit.Password)
        self.lay.addRow("Пользователь",self.userEdit)
        self.lay.addRow("Пароль",self.passEdit)
        self.okBtn = QPushButton('Ok')
        self.okBtn.setDefault(True)
        self.cancelBtn = QPushButton('Отмена')
        self.btnLay.addWidget(self.okBtn)
        self.btnLay.addWidget(self.cancelBtn)
        self.okBtn.clicked.connect(self.accept)
        self.cancelBtn.clicked.connect(self.reject)

    def __getattr__(self, name):
        if name == 'user':
            return self.userEdit.text()
        if name == 'password':
            return self.passEdit.text()
        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name == 'user':
            self.userEdit.setText(value)
            return
        if name == 'password':
            self.passEdit.setText(value)
            return
        if name == 'dbname':
            self.setWindowTitle(value)
            return
        super().__setattr__(name,value)
        

def openDatabase(dbini):
    db = QSqlDatabase.database(dbini)
    if not db.isValid():
        ini = QSettings(dbini, QSettings.IniFormat)
        ini.setIniCodec("utf-8")
        ini.beginGroup("DB")
        dbdriver = ini.value("Driver")
        dbname = str(ini.value("DBName"))
        inipath = os.path.split(os.path.abspath(dbini))[0]
        dbname = dbname.format(inipath=inipath)
        dbuser = ini.value("DBUser")
        dbpass = ini.value("DBPass")
        needPrompt = ini.value("PromptLogin")
        if needPrompt:
            dlg = DBLoginDlg()
            dlg.user = dbuser
            dlg.password = dbpass
            dlg.dbname = os.path.basename(dbini)
            if not dlg.exec():
                return None
            dbuser = dlg.user
            dbpass = dlg.password
        startSql = ini.value("StartSQL","")
        ini.endGroup()
        db = QSqlDatabase.addDatabase(dbdriver,dbini)
        db.setDatabaseName(dbname);
        db.setUserName(dbuser)
        db.setPassword(dbpass)
        if not db.open():
            print("Error ({0}) on open DB '{2}'\n{1}".format(
                db.lastError().nativeErrorCode(),
                db.lastError().text(),
                dbini))
            db = None
            QSqlDatabase.removeDatabase(dbini)
            return None
        if startSql != None and startSql != "":
            QSqlQuery(startSql, db).exec_()
    return db

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBLoginDlg()
    ex.user = 'abc'
    ex.password = 'abc'
    ex.exec()
    print(ex.user, ex.password)

    #sys.exit(app.exec_())
