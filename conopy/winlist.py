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


class WinList(QListWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        if not self.parent() is None:
            self.main = self.parent().parent()
            self.winsParent = self.main.centralWidget()
            self.winsParent.subWindowActivated.connect(self.showActivated)
            self.winsParent.installEventFilter(self)
        else:
            self.main = None
            self.winsParent = None
        self.tid = self.startTimer(1000)
        self.needCheckList = True
        self.itemClicked.connect(self.itemClick)

    def itemClick(self, item):
        w = item.data(Qt.UserRole)
        if self.winsParent is None:
            return
        self.winsParent.setActiveSubWindow(w)
        

    def timerEvent(self, event):
        if event.timerId() == self.tid:
            self.checkList()
        else:
            super().timerEvent(event)

    def showActivated(self,win):
        self.needCheckList = True

    def checkList(self):
        if self.needCheckList:
            self.needCheckList = False;
            self.fillList()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.ChildAdded or event.type() == QEvent.ChildRemoved:
            self.needCheckList = True
        return super().eventFilter(obj, event)

    def fillList(self):
        self.clear()
        if self.winsParent is None:
            return
        wins = self.winsParent.subWindowList()
        for w in wins:
            i = QListWidgetItem(w.windowTitle(), self)
            i.setData(Qt.UserRole, w)
        

if __name__ == '__main__':
    import tasktree
##    tasktree.run('../data/tasks.txt')
        
    app = QApplication(sys.argv)
    w = WinList()
    w.show()

##    view = MainWindow(tasksFile)
##    view.setWindowTitle("Conopy")
##    app.focusedTaskWindow = view.focusedTaskWindow
##    
##    view.show()
    sys.exit(app.exec_())
