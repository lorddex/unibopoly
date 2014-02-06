# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wqlResult.ui'
#
# Created: Wed Apr 23 16:45:46 2008
#      by: PyQt4 UI code generator 4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_WQLResultDialog(object):
    def setupUi(self, WQLResultDialog):
        WQLResultDialog.setObjectName("WQLResultDialog")
        WQLResultDialog.setWindowModality(QtCore.Qt.NonModal)
        WQLResultDialog.resize(QtCore.QSize(QtCore.QRect(0,0,671,568).size()).expandedTo(WQLResultDialog.minimumSizeHint()))

        self.line = QtGui.QFrame(WQLResultDialog)
        self.line.setGeometry(QtCore.QRect(10,505,651,21))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")

        self.pushButtonClose = QtGui.QPushButton(WQLResultDialog)
        self.pushButtonClose.setGeometry(QtCore.QRect(300,530,83,27))
        self.pushButtonClose.setObjectName("pushButtonClose")

        self.listWidgetResults = QtGui.QListWidget(WQLResultDialog)
        self.listWidgetResults.setGeometry(QtCore.QRect(10,110,651,391))
        self.listWidgetResults.setObjectName("listWidgetResults")

        self.labelResults = QtGui.QLabel(WQLResultDialog)
        self.labelResults.setGeometry(QtCore.QRect(10,90,641,18))
        self.labelResults.setObjectName("labelResults")

        self.labelQuery = QtGui.QTextEdit(WQLResultDialog)
        self.labelQuery.setEnabled(False)
        self.labelQuery.setGeometry(QtCore.QRect(60,10,591,75))
        self.labelQuery.setObjectName("labelQuery")

        self.label = QtGui.QLabel(WQLResultDialog)
        self.label.setGeometry(QtCore.QRect(10,40,57,18))
        self.label.setObjectName("label")

        self.retranslateUi(WQLResultDialog)
        QtCore.QObject.connect(self.pushButtonClose,QtCore.SIGNAL("clicked()"),WQLResultDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(WQLResultDialog)

    def retranslateUi(self, WQLResultDialog):
        WQLResultDialog.setWindowTitle(QtGui.QApplication.translate("WQLResultDialog", "WQL Result", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonClose.setText(QtGui.QApplication.translate("WQLResultDialog", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.labelResults.setText(QtGui.QApplication.translate("WQLResultDialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WQLResultDialog", "WQL:", None, QtGui.QApplication.UnicodeUTF8))

