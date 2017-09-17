#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from conopy.toolbar import ToolBar
import sys
import importlib

class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

    def proc(self):
        return self.data(2)


class TreeModel(QAbstractItemModel):
    def __init__(self, data, parent=None):
        super(TreeModel, self).__init__(parent)

        self.rootItem = TreeItem(("Title", "Summary"))
        self.setupModelData(data.split('\n'), self.rootItem)


    def columnCount(self, parent = QModelIndex()):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid():
            return None

        #if role != Qt.DisplayRole and role != Qt.UserRole :
        #    return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            return item.data(index.column())

        if role == Qt.UserRole:
            return item.proc()
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent = QModelIndex()):
        if not self.hasIndex(row, column, parent):
            print('no index',row, column, parent)
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent = QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setupModelData(self, lines, parent):
        parents = [parent]
        indentations = [0]

        number = 0

        while number < len(lines):
            position = 0
            l = str(lines[number],'utf-8')
            #print(l)
            while position < len(l):
                if l[position] != ' ':
                    break
                position += 1

            lineData = l[position:].strip()

            if lineData:
                # Read the column data from the rest of the line.
                columnData = [s for s in lineData.split('\t') if s]

                if position > indentations[-1]:
                    # The last child of the current parent is now the new
                    # parent unless the current parent has no children.

                    if parents[-1].childCount() > 0:
                        parents.append(parents[-1].child(parents[-1].childCount() - 1))
                        indentations.append(position)

                else:
                    while position < indentations[-1] and len(parents) > 0:
                        parents.pop()
                        indentations.pop()

                # Append a new item to the current parent's list of children.
                item = TreeItem(columnData, parents[-1])
                parents[-1].appendChild(item)

            number += 1


class TreeWidget(QTreeView):
    def __init__(self, parent=None):
        super(TreeWidget, self).__init__(parent)
        #self.doubleClicked.connect(self.handle_dblclick)
        
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.mdiArea = QMdiArea(self)
        self.setCentralWidget(self.mdiArea)
        self.mainMenu = QMenuBar(self)
        self.setMenuBar(self.mainMenu)
        m = self.mainMenu.addMenu("Window")
        a = m.addAction("Cascade windows")
        a.triggered.connect(self.mdiArea.cascadeSubWindows)
        
        self.treePanel = QDockWidget("Дерево задач", self)
        w = QWidget(self.treePanel)
        lay = QVBoxLayout(w)
        lay.setSpacing(1)
        lay.setContentsMargins(1,1,1,1)
        w.setLayout(lay)
        self.tree = TreeWidget(self.treePanel)
        lay.addWidget(self.tree)
        edit = QTextEdit(w)
        lay.addWidget(edit)
        
        self.treePanel.setWidget(w)
        self.tree.activated.connect(self.handle_dblclick)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.treePanel)
        
        self.tools = ToolBar("tools.ini", self)
        self.addToolBar(self.tools)
        

    def focusedTaskWindow(self):
        sub = self.mdiArea.currentSubWindow()
        if sub != None:
            return sub.widget()
        return None

    def handle_dblclick(self, index):
        try:
            iniFile = index.data(Qt.UserRole)
            if iniFile != None:
                ini = QSettings(iniFile, QSettings.IniFormat)
                ini.setIniCodec("utf-8")
                exeClass = ["conopy.sqlexecutor", "PyExecutor"]
                if "Common" in ini.childGroups():
                    ini.beginGroup("Common")
                    exeClass = ini.value("Executor", exeClass)
                    ini.endGroup()
                module = importlib.import_module(exeClass[0])
                ex = eval("module.%s(iniFile)" % exeClass[1])
                
                #proc = proc.strip()
                #ex = PyExecutor(proc)
                if ex != None:
                    self.mdiArea.addSubWindow(ex)
                    ex.show()
        except:
            print(str(sys.exc_info()[1]))
            
            

view = None

def run():
    import os
    import PyQt5
    import sys

    pyqt = os.path.dirname(PyQt5.__file__)
    QApplication.addLibraryPath(os.path.join(pyqt, "Qt", "plugins"))

    app = QApplication(sys.argv)

    f = QFile('tasks.txt')
    f.open(QIODevice.ReadOnly)
    model = TreeModel(f.readAll())
    f.close()

    view = MainWindow()
    view.setWindowTitle("Conopy")
    view.tree.setModel(model)
    view.tree.expandAll()
    view.tree.setColumnHidden(1,True)
    app.focusedTaskWindow = view.focusedTaskWindow
    
    view.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
    
    
