#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
if __package__ is None or __package__ == '':
    from sqlexecutor import SqlExecutor
    import meshandler, dbpool, sqlmodels
else:
    from . import (dbpool, sqlmodels)
    from .sqlexecutor import SqlExecutor

class MSExecutor(SqlExecutor):
    def __init__(self, iniFile, parent=None):
        super().__init__(iniFile, parent)

    def createModel(self, parent=None):
        return sqlmodels.MSSQLModel(parent)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MSExecutor("../local/test-sql.ini")
    ex.show()
    sys.exit(app.exec_())
