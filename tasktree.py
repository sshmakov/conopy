from PyQt5 import QtCore, QtGui, QtWidgets
from executor import PyExecutor

##try:
##    import simpletreemodel_rc3
##except ImportError:
##    import simpletreemodel_rc2
from toolbar import ToolBar

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


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, data, parent=None):
        super(TreeModel, self).__init__(parent)

        self.rootItem = TreeItem(("Title", "Summary"))
        self.setupModelData(data.split('\n'), self.rootItem)


    def columnCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        #if role != QtCore.Qt.DisplayRole and role != QtCore.Qt.UserRole :
        #    return None

        item = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())

        if role == QtCore.Qt.UserRole:
            return item.proc()
        return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent = QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            print('no index',row, column, parent)
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent = QtCore.QModelIndex()):
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


class TreeWidget(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        super(TreeWidget, self).__init__(parent)
        #self.doubleClicked.connect(self.handle_dblclick)
        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.mdiArea = QtWidgets.QMdiArea(self)
        self.setCentralWidget(self.mdiArea)
        self.mainMenu = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.mainMenu)
        m = self.mainMenu.addMenu("Window")
        a = m.addAction("Cascade windows")
        a.triggered.connect(self.mdiArea.cascadeSubWindows)
        
        self.treePanel = QtWidgets.QDockWidget("Дерево задач", self)
        w = QtWidgets.QWidget(self.treePanel)
        lay = QtWidgets.QVBoxLayout(w)
        lay.setSpacing(1)
        lay.setContentsMargins(1,1,1,1)
        w.setLayout(lay)
        self.tree = TreeWidget(self.treePanel)
        lay.addWidget(self.tree)
        edit = QtWidgets.QTextEdit(w)
        lay.addWidget(edit)
        
        self.treePanel.setWidget(w)
        self.tree.activated.connect(self.handle_dblclick)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.treePanel)
        
        self.tools = ToolBar(self)
        self.addToolBar(self.tools)
        

    def focusedTaskWindow(self):
        sub = self.mdiArea.currentSubWindow()
        if sub != None:
            return sub.widget()
        return None

    def handle_dblclick(self, index):
        proc = index.data(QtCore.Qt.UserRole)
        if proc != None:
            proc = proc.strip()
            ex = PyExecutor(proc)
            self.mdiArea.addSubWindow(ex)
            ex.show()
            

view = None

def focusedWindow():
    if view == None:
        return None
    return view.focusedTaskWindow()

if __name__ == '__main__':

    import os
    import PyQt5
    import sys

    pyqt = os.path.dirname(PyQt5.__file__)
    QtWidgets.QApplication.addLibraryPath(os.path.join(pyqt, "Qt/plugins"))
    app = QtWidgets.QApplication(sys.argv)
    app.focusedTaskWindow = focusedWindow

    f = QtCore.QFile('tasks.txt')
    f.open(QtCore.QIODevice.ReadOnly)
    model = TreeModel(f.readAll())
    f.close()

    view = MainWindow()
    view.setWindowTitle("Simple Tree Model")
    view.tree.setModel(model)
    view.tree.expandAll()
    view.tree.setColumnHidden(1,True)
    
    view.show()
    sys.exit(app.exec_())

    
    
