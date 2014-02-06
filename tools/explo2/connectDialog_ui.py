# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'connectDialog.ui'
#
# Created: Wed Apr 23 16:45:45 2008
#      by: PyQt4 UI code generator 4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_DialogConnect(object):
    def setupUi(self, DialogConnect):
        DialogConnect.setObjectName("DialogConnect")
        DialogConnect.setWindowModality(QtCore.Qt.ApplicationModal)
        DialogConnect.setEnabled(True)
        DialogConnect.resize(QtCore.QSize(QtCore.QRect(0,0,545,154).size()).expandedTo(DialogConnect.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(DialogConnect)
        self.buttonBox.setGeometry(QtCore.QRect(360,110,171,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.label = QtGui.QLabel(DialogConnect)
        self.label.setGeometry(QtCore.QRect(10,10,116,18))
        self.label.setObjectName("label")

        self.label_2 = QtGui.QLabel(DialogConnect)
        self.label_2.setGeometry(QtCore.QRect(10,40,116,18))
        self.label_2.setObjectName("label_2")

        self.label_3 = QtGui.QLabel(DialogConnect)
        self.label_3.setGeometry(QtCore.QRect(10,70,116,18))
        self.label_3.setObjectName("label_3")

        self.line = QtGui.QFrame(DialogConnect)
        self.line.setGeometry(QtCore.QRect(10,90,521,16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")

        self.lineEditSSName = QtGui.QLineEdit(DialogConnect)
        self.lineEditSSName.setGeometry(QtCore.QRect(150,10,381,23))
        self.lineEditSSName.setObjectName("lineEditSSName")

        self.lineEditIPAddr = QtGui.QLineEdit(DialogConnect)
        self.lineEditIPAddr.setGeometry(QtCore.QRect(150,40,381,23))
        self.lineEditIPAddr.setObjectName("lineEditIPAddr")

        self.lineEditPort = QtGui.QLineEdit(DialogConnect)
        self.lineEditPort.setGeometry(QtCore.QRect(150,70,381,23))
        self.lineEditPort.setObjectName("lineEditPort")

        self.comboBoxPredef = QtGui.QComboBox(DialogConnect)
        self.comboBoxPredef.setGeometry(QtCore.QRect(11,110,351,31))
        self.comboBoxPredef.setObjectName("comboBoxPredef")

        self.retranslateUi(DialogConnect)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),DialogConnect.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),DialogConnect.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogConnect)

    def retranslateUi(self, DialogConnect):
        DialogConnect.setWindowTitle(QtGui.QApplication.translate("DialogConnect", "SIB Connection", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("DialogConnect", "SmartSpace Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("DialogConnect", "IP Address", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("DialogConnect", "Port", None, QtGui.QApplication.UnicodeUTF8))

