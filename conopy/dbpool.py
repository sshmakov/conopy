#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os
from PyQt5.QtCore import *
#from PyQt5.QtWidgets import *
from PyQt5.QtSql import *

def openDatabase(dbini):
    db = QSqlDatabase.database(dbini)
    if not db.isValid():
        ini = QSettings(dbini, QSettings.IniFormat)
        ini.setIniCodec("utf-8")
        ini.beginGroup("DB")
        dbdriver = ini.value("Driver")
        dbname = str(ini.value("DBName")).format(
            inipath=os.path.split(os.path.abspath(dbini))[0])
        dbuser = ini.value("DBUser")
        dbpass = ini.value("DBPass")
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
