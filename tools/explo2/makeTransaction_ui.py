# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'makeTransaction.ui'
#
# Created: Wed Apr 23 16:45:46 2008
#      by: PyQt4 UI code generator 4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_DialogMakeTransaction(object):
    def setupUi(self, DialogMakeTransaction):
        DialogMakeTransaction.setObjectName("DialogMakeTransaction")
        DialogMakeTransaction.resize(QtCore.QSize(QtCore.QRect(0,0,806,463).size()).expandedTo(DialogMakeTransaction.minimumSizeHint()))

        self.pushButtonAdd = QtGui.QPushButton(DialogMakeTransaction)
        self.pushButtonAdd.setGeometry(QtCore.QRect(80,380,80,27))
        self.pushButtonAdd.setObjectName("pushButtonAdd")

        self.label = QtGui.QLabel(DialogMakeTransaction)
        self.label.setGeometry(QtCore.QRect(10,290,57,18))
        self.label.setObjectName("label")

        self.label_2 = QtGui.QLabel(DialogMakeTransaction)
        self.label_2.setGeometry(QtCore.QRect(10,320,61,18))
        self.label_2.setObjectName("label_2")

        self.label_3 = QtGui.QLabel(DialogMakeTransaction)
        self.label_3.setGeometry(QtCore.QRect(10,350,57,18))
        self.label_3.setObjectName("label_3")

        self.lineEditSubject = QtGui.QLineEdit(DialogMakeTransaction)
        self.lineEditSubject.setGeometry(QtCore.QRect(410,290,301,27))
        self.lineEditSubject.setObjectName("lineEditSubject")

        self.lineEditPredicate = QtGui.QLineEdit(DialogMakeTransaction)
        self.lineEditPredicate.setGeometry(QtCore.QRect(410,320,301,27))
        self.lineEditPredicate.setObjectName("lineEditPredicate")

        self.lineEditObject = QtGui.QLineEdit(DialogMakeTransaction)
        self.lineEditObject.setGeometry(QtCore.QRect(410,350,301,27))
        self.lineEditObject.setObjectName("lineEditObject")

        self.label_4 = QtGui.QLabel(DialogMakeTransaction)
        self.label_4.setGeometry(QtCore.QRect(10,380,57,18))
        self.label_4.setObjectName("label_4")

        self.comboBoxSubjectNS = QtGui.QComboBox(DialogMakeTransaction)
        self.comboBoxSubjectNS.setGeometry(QtCore.QRect(80,290,321,26))
        self.comboBoxSubjectNS.setObjectName("comboBoxSubjectNS")

        self.comboBoxPredicateNS = QtGui.QComboBox(DialogMakeTransaction)
        self.comboBoxPredicateNS.setGeometry(QtCore.QRect(80,320,321,26))
        self.comboBoxPredicateNS.setObjectName("comboBoxPredicateNS")

        self.comboBoxObjectNS = QtGui.QComboBox(DialogMakeTransaction)
        self.comboBoxObjectNS.setGeometry(QtCore.QRect(80,350,321,26))
        self.comboBoxObjectNS.setObjectName("comboBoxObjectNS")

        self.pushButtonGenUUID4Subject = QtGui.QPushButton(DialogMakeTransaction)
        self.pushButtonGenUUID4Subject.setGeometry(QtCore.QRect(680,260,123,27))
        self.pushButtonGenUUID4Subject.setObjectName("pushButtonGenUUID4Subject")

        self.radioButtonURI = QtGui.QRadioButton(DialogMakeTransaction)
        self.radioButtonURI.setGeometry(QtCore.QRect(500,380,99,23))
        self.radioButtonURI.setChecked(True)
        self.radioButtonURI.setObjectName("radioButtonURI")

        self.radioButtonLiteral = QtGui.QRadioButton(DialogMakeTransaction)
        self.radioButtonLiteral.setGeometry(QtCore.QRect(550,380,99,23))
        self.radioButtonLiteral.setObjectName("radioButtonLiteral")

        self.line = QtGui.QFrame(DialogMakeTransaction)
        self.line.setGeometry(QtCore.QRect(10,400,791,21))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")

        self.pushButton_7 = QtGui.QPushButton(DialogMakeTransaction)
        self.pushButton_7.setGeometry(QtCore.QRect(10,420,80,27))
        self.pushButton_7.setObjectName("pushButton_7")

        self.pushButtonClose = QtGui.QPushButton(DialogMakeTransaction)
        self.pushButtonClose.setGeometry(QtCore.QRect(720,420,80,27))
        self.pushButtonClose.setObjectName("pushButtonClose")

        self.checkBox = QtGui.QCheckBox(DialogMakeTransaction)
        self.checkBox.setGeometry(QtCore.QRect(100,420,83,23))
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")

        self.label_5 = QtGui.QLabel(DialogMakeTransaction)
        self.label_5.setGeometry(QtCore.QRect(80,270,178,18))
        self.label_5.setObjectName("label_5")

        self.label_6 = QtGui.QLabel(DialogMakeTransaction)
        self.label_6.setGeometry(QtCore.QRect(410,270,126,18))
        self.label_6.setObjectName("label_6")

        self.pushButtonPopulate = QtGui.QPushButton(DialogMakeTransaction)
        self.pushButtonPopulate.setGeometry(QtCore.QRect(320,420,94,27))
        self.pushButtonPopulate.setObjectName("pushButtonPopulate")

        self.pushButtonPopulateNS = QtGui.QPushButton(DialogMakeTransaction)
        self.pushButtonPopulateNS.setGeometry(QtCore.QRect(420,420,150,27))
        self.pushButtonPopulateNS.setObjectName("pushButtonPopulateNS")

        self.checkBoxSubjectUse = QtGui.QCheckBox(DialogMakeTransaction)
        self.checkBoxSubjectUse.setGeometry(QtCore.QRect(720,290,91,23))
        self.checkBoxSubjectUse.setChecked(True)
        self.checkBoxSubjectUse.setTristate(False)
        self.checkBoxSubjectUse.setObjectName("checkBoxSubjectUse")

        self.checkBoxPredicateUse = QtGui.QCheckBox(DialogMakeTransaction)
        self.checkBoxPredicateUse.setGeometry(QtCore.QRect(720,320,91,23))
        self.checkBoxPredicateUse.setChecked(True)
        self.checkBoxPredicateUse.setTristate(False)
        self.checkBoxPredicateUse.setObjectName("checkBoxPredicateUse")

        self.checkBoxObjectUse = QtGui.QCheckBox(DialogMakeTransaction)
        self.checkBoxObjectUse.setGeometry(QtCore.QRect(720,350,91,23))
        self.checkBoxObjectUse.setChecked(True)
        self.checkBoxObjectUse.setTristate(False)
        self.checkBoxObjectUse.setObjectName("checkBoxObjectUse")

        self.listWidgetTriples = QtGui.QTableWidget(DialogMakeTransaction)
        self.listWidgetTriples.setGeometry(QtCore.QRect(10,10,791,241))
        self.listWidgetTriples.setObjectName("listWidgetTriples")

        self.label_7 = QtGui.QLabel(DialogMakeTransaction)
        self.label_7.setGeometry(QtCore.QRect(410,380,126,18))
        self.label_7.setObjectName("label_7")

        self.retranslateUi(DialogMakeTransaction)
        QtCore.QObject.connect(self.pushButtonClose,QtCore.SIGNAL("clicked()"),DialogMakeTransaction.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogMakeTransaction)

    def retranslateUi(self, DialogMakeTransaction):
        DialogMakeTransaction.setWindowTitle(QtGui.QApplication.translate("DialogMakeTransaction", "Make Transaction", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonAdd.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Subject", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Predicate", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Object", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBoxPredicateNS.setToolTip(QtGui.QApplication.translate("DialogMakeTransaction", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This contains a list of namespaces and property URIs which get prepended to the user entered data</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonGenUUID4Subject.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Subject URI UUID4", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonURI.setText(QtGui.QApplication.translate("DialogMakeTransaction", "URI", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonLiteral.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Literal", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_7.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Insert", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonClose.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Atomic", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Existing URIs + Namespaces", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("DialogMakeTransaction", "User entered data", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonPopulate.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Populate fully", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonPopulateNS.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Populate namespaces", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxSubjectUse.setText(QtGui.QApplication.translate("DialogMakeTransaction", "use uri/ns", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxPredicateUse.setText(QtGui.QApplication.translate("DialogMakeTransaction", "use uri/ns", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxObjectUse.setText(QtGui.QApplication.translate("DialogMakeTransaction", "use uri/ns", None, QtGui.QApplication.UnicodeUTF8))
        self.listWidgetTriples.clear()
        self.listWidgetTriples.setColumnCount(0)
        self.listWidgetTriples.setRowCount(0)
        self.label_7.setText(QtGui.QApplication.translate("DialogMakeTransaction", "Object Type:", None, QtGui.QApplication.UnicodeUTF8))

