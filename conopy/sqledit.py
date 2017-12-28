#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os, re
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
import meshandler
#dbpool)



def loadCSS(file):
    allStyles = {}
    style = {}
    cname = None
    inComment = False
    fd = open(file,'r',encoding='utf-8')
    for line in fd:
        l = line.strip()
        while l != "":
            if inComment:
                pos = l.find("*/")
                if pos != -1:
                    l = l[pos+2:].strip()
                    inComment = False
                else:
                    l = ""
                continue
            if l.startswith("/*"):
                inComment = True
                l = l[2:].strip()
                continue
            if l.endswith('{'):
                cname = l[:-1].strip()
                style = {}
                l = ""
                continue
            elif l.endswith('}'):
                if len(style) != 0 and not cname is None:
                    allStyles[cname] = style
                cname = None
                cname = l[:-1].strip()
                l = ""
                continue
            if l == "":
                break;
            ar = l.split(':',1)
            if len(ar) != 2:
                break;
            key, v = ar
            v = v.strip()
            if v.endswith(';'):
                v = v[:-1]
            style[key] = v
            l = ""
    return allStyles

def css2format(css, fmt=None):
    if fmt is None:
        fmt = QTextCharFormat();
    v = css.get('font-style')
    if v:
        fmt.setFontItalic(v in ('oblique', 'italic'))
    v = css.get('font-weight')
    if v:
        fmt.setFontWeight(
            QFont.Bold if v == 'bold' else
            int(v) / 10 if v.isdigit() else 
            QFont.Normal)
    v = css.get('color')
    if v:
        fmt.setForeground(QColor(v))
    v = css.get('background')
    if v:
        fmt.setBackground(QColor(v))
    v = css.get('text-decoration')
    if v:
        fmt.setFontUnderline(v == 'underline')
    v = css.get('text-decoration-color')
    if v:
        fmt.setUnderlineColor(QColor(v))
    v = css.get('text-transform')
    if v:
        fmt.setFontCapitalization(
            QFont.AllUppercase if v == 'uppercase' else
            QFont.AllLowercase if v == 'lowercase' else
            QFont.Capitalize if v == 'capitalize' else
            QFont.MixedCase)
    return fmt

def nearFile(filename, fromFile):
    return os.path.join(
        os.path.split(
            os.path.abspath(fromFile))[0], filename)

class SQLSyntaxHighlighter(QSyntaxHighlighter):
    stringRules = []
    blockRules = []

    def __init__(self, te):
        super().__init__(te)

    def loadStyles(self, iniFile):
        ini = QSettings(iniFile, QSettings.IniFormat)
        ini.beginGroup("Format")
        self.allStyles = {}
        css = ini.value("styles")
        if type(css) is list:
            for f in css:
                a = loadCSS(nearFile(f, iniFile))
                self.allStyles = {**self.allStyles, **a}
        elif css:
            self.allStyles = loadCSS(nearFile(css, iniFile))
        fStr = ini.value("flags","")
        self.flags = 0
        for f in fStr:
            if f == 'i': self.flags = self.flags | re.I
            elif f == 's': self.flags = self.flags | re.S
            elif f == 'l': self.flags = self.flags | re.L
            elif f == 'm': self.flags = self.flags | re.M
        self.defaultStyle = ini.value('defaultStyle','')
        ini.endGroup()

        self.stringRules = []
        ini.beginGroup("StringRules")
        for key in ini.childKeys():
            f = ini.value(key)
            rule = f[0];
            if rule.startswith('@'):
                keys = self.readKeywords(nearFile(rule[1:],iniFile))
                s = None
                for k in keys:
                    s = (s + '|' if s else "") + '\\b'+k+ '\\b'
                rule = re.compile(s, self.flags)
            else:
                rule = re.compile(f[0], self.flags)
            cnames = f[1].split(' ')
            self.stringRules.append([rule, cnames])
        ini.endGroup()

        self.blockRules = []
        ini.beginGroup("BlockRules")
        for key in ini.childKeys():
            f = ini.value(key)
            ruleStart = re.compile(f[0], self.flags)
            ruleEnd = re.compile(f[1], self.flags)
            cnames = f[2].split(' ')
            self.blockRules.append([rule, cnames])
        ini.endGroup()

    def readKeywords(self, file):
        res = []
        fd = open(file, encoding='utf-8')
        for l in fd:
            l = l.strip()
            if l == "" or l.startswith(':'):
                continue
            res.append(l)
        return res

    def classesFormat(self, cnames):
        fmt = QTextCharFormat();
        for c in cnames:
            css = self.allStyles.get('.'+c)
            if css:
                fmt = css2format(css, fmt)
        return fmt

    def highlightBlock(self, text):
        for r in self.stringRules:
            rule, cnames = r
            for m in rule.finditer(text):
                fmt = self.classesFormat(cnames)
                self.setFormat(m.start(), m.end()-m.start(), fmt)
        

class SqlEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.edit = QTextEdit(self)
        self.lay = QVBoxLayout(self)
        self.lay.addWidget(self.edit)
        self.btnbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,self)
        self.lay.addWidget(self.btnbox)
        self.btnbox.clicked.connect(self.btnClick)
        self.syn = SQLSyntaxHighlighter(self.edit)
        self.syn.loadStyles('syntax/sql.ini')
        font = QFont("Courier New", 10)
        self.edit.setFont(font)

        self.readText()

    def readText(self):
        self.win = self.focusTaskWindow()
        if not self.win:
            return;
        
        
    def btnClick(self, btn):
        if self.buttonRole(btn) == QDialogButtonBox.AcceptRole:
            self.saveText()
        else:
            self.cancel()

    def saveText(self):
        pass

    def cancel(self):
        pass

    def focusTaskWindow():
        try:
            return QApplication.instance().focusedTaskWindow()
        except:
##            print(str(sys.exc_info()[1]))
            return None

def run():
    win = 


if __name__ == '__main__':
    app = QApplication(sys.argv)
    edit = SqlEditor()
    edit.show()

    sys.exit(app.exec_())
    



"""            
        pos = self.rg_comment.search(text)
        if not pos is None:
            self.setFormat(pos, len(text), Qt.green)
            return
        self.setFormat(0, len(text), Qt.black)

    def formatBlock(self, cnames, startMask, endMask)
          mf = QTextCharFormat();
          mf.setForeground(Qt::red);

  QRegExp startExpression("/\\*");
  QRegExp endExpression("\\*/");

  setCurrentBlockState(0);

  int startIndex = 0;
  if (previousBlockState() != 1)
      startIndex = text.indexOf(startExpression);

  while (startIndex >= 0) {
     int endIndex = text.indexOf(endExpression, startIndex);
     int commentLength;
     if (endIndex == -1) {
         setCurrentBlockState(1);
         commentLength = text.length() - startIndex;
     } else {
         commentLength = endIndex - startIndex
                         + endExpression.matchedLength();
     }
     setFormat(startIndex, commentLength, multiLineCommentFormat);
     startIndex = text.indexOf(startExpression,
                               startIndex + commentLength);
  }
"""
