import sys
from PyQt5 import QtCore, QtWidgets

def qt_message_handler(mode, context, message):
    if mode == QtCore.QtInfoMsg:
        mode = 'INFO'
    elif mode == QtCore.QtWarningMsg:
        mode = 'WARNING'
    elif mode == QtCore.QtCriticalMsg:
        mode = 'CRITICAL'
    elif mode == QtCore.QtFatalMsg:
        mode = 'FATAL'
    else:
        mode = 'DEBUG'
    print('qt_message_handler: line: %d, func: %s(), file: %s' % (
          context.line, context.function, context.file))
    print('  %s: %s\n' % (mode, message))

QtCore.qInstallMessageHandler(qt_message_handler)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    QtCore.qDebug('something informative')
    win = QtWidgets.QMainWindow()
    # trigger a Qt debug message
    win.setLayout(QtWidgets.QVBoxLayout())
