# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'explorer.ui'
#
# Created: Wed Apr 23 16:45:45 2008
#      by: PyQt4 UI code generator 4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainUI(object):
    def setupUi(self, MainUI):
        MainUI.setObjectName("MainUI")
        MainUI.resize(QtCore.QSize(QtCore.QRect(0,0,1175,674).size()).expandedTo(MainUI.minimumSizeHint()))

        self.exitButton = QtGui.QPushButton(MainUI)
        self.exitButton.setGeometry(QtCore.QRect(780,640,83,27))
        self.exitButton.setObjectName("exitButton")

        self.line = QtGui.QFrame(MainUI)
        self.line.setGeometry(QtCore.QRect(10,620,1151,16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")

        self.label_2 = QtGui.QLabel(MainUI)
        self.label_2.setGeometry(QtCore.QRect(10,563,121,18))
        self.label_2.setObjectName("label_2")

        self.label_3 = QtGui.QLabel(MainUI)
        self.label_3.setGeometry(QtCore.QRect(10,560,101,18))
        self.label_3.setObjectName("label_3")

        self.lineSPARQL = QtGui.QLineEdit(MainUI)
        self.lineSPARQL.setGeometry(QtCore.QRect(110,560,990,30))    #WQLFrame
        self.lineSPARQL.setObjectName("lineSPARQL")

        self.SPARQLButton = QtGui.QPushButton(MainUI)
        self.SPARQLButton.setGeometry(QtCore.QRect(1110,560,50,30))
        self.SPARQLButton.setObjectName("SPARQLButton")

        #self.lineEditWQLBody = QtGui.QLineEdit(MainUI)
        #self.lineEditWQLBody.setGeometry(QtCore.QRect(130,560,731,23))
        #self.lineEditWQLBody.setObjectName("lineEditWQLBody")

        self.line_2 = QtGui.QFrame(MainUI)
        self.line_2.setGeometry(QtCore.QRect(10,510,851,16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")

        self.pushButtonListAllAsTriples = QtGui.QPushButton(MainUI)
        self.pushButtonListAllAsTriples.setGeometry(QtCore.QRect(10,480,102,27))
        self.pushButtonListAllAsTriples.setObjectName("pushButtonListAllAsTriples")

        self.pushButtonListClassesOnly = QtGui.QPushButton(MainUI)
        self.pushButtonListClassesOnly.setGeometry(QtCore.QRect(120,480,113,27))
        self.pushButtonListClassesOnly.setObjectName("pushButtonListClassesOnly")

        self.pushButtonListPropertiesOnly = QtGui.QPushButton(MainUI)
        self.pushButtonListPropertiesOnly.setGeometry(QtCore.QRect(240,480,130,27))
        self.pushButtonListPropertiesOnly.setObjectName("pushButtonListPropertiesOnly")

        #self.pushButtonQuery = QtGui.QPushButton(MainUI)
        #self.pushButtonQuery.setGeometry(QtCore.QRect(10,590,83,27))
        #self.pushButtonQuery.setObjectName("pushButtonQuery")

        self.pushButtonCloseQueryWindows = QtGui.QPushButton(MainUI)
        #self.pushButtonCloseQueryWindows.setGeometry(QtCore.QRect(260,590,160,27))
        #self.pushButtonCloseQueryWindows.setObjectName("pushButtonCloseQueryWindows")

        self.pushButtonConnect = QtGui.QPushButton(MainUI)
        self.pushButtonConnect.setGeometry(QtCore.QRect(510,640,83,27))
        self.pushButtonConnect.setObjectName("pushButtonConnect")

        self.pushButtonConnectionDetails = QtGui.QPushButton(MainUI)
        self.pushButtonConnectionDetails.setGeometry(QtCore.QRect(730,480,128,27))
        self.pushButtonConnectionDetails.setObjectName("pushButtonConnectionDetails")

        self.treeWidgetState = QtGui.QTreeWidget(MainUI)
        self.treeWidgetState.setGeometry(QtCore.QRect(10,10,1141,461))
        self.treeWidgetState.setObjectName("treeWidgetState")

        self.pushButtonFullList = QtGui.QPushButton(MainUI)
        self.pushButtonFullList.setGeometry(QtCore.QRect(380,480,110,27))
        self.pushButtonFullList.setObjectName("pushButtonFullList")

        #self.comboCommon = QtGui.QComboBox(MainUI)
        #self.comboCommon.setGeometry(QtCore.QRect(631,590,231,26))
        #self.comboCommon.setObjectName("comboCommon")

        self.label_4 = QtGui.QLabel(MainUI)
        self.label_4.setGeometry(QtCore.QRect(510,590,109,20))
        self.label_4.setObjectName("label_4")

        #self.pushButtonMakeTransaction = QtGui.QPushButton(MainUI)
        #self.pushButtonMakeTransaction.setGeometry(QtCore.QRect(10,640,119,27))
        #self.pushButtonMakeTransaction.setObjectName("pushButtonMakeTransaction")

        self.line_3 = QtGui.QFrame(MainUI)
        self.line_3.setGeometry(QtCore.QRect(590,630,20,41))
        self.line_3.setFrameShape(QtGui.QFrame.VLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName("line_3")

        #self.pushButtonSubscribe = QtGui.QPushButton(MainUI)
        #self.pushButtonSubscribe.setGeometry(QtCore.QRect(100,590,91,27))
        #self.pushButtonSubscribe.setObjectName("pushButtonSubscribe")

        self.pushButtonShowAsGraph = QtGui.QPushButton(MainUI)
        self.pushButtonShowAsGraph.setGeometry(QtCore.QRect(619,480,104,27))
        self.pushButtonShowAsGraph.setObjectName("pushButtonShowAsGraph")

        self.line_4 = QtGui.QFrame(MainUI)
        self.line_4.setGeometry(QtCore.QRect(490,630,20,41))
        self.line_4.setFrameShape(QtGui.QFrame.VLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName("line_4")

        self.pushButtonHelp = QtGui.QPushButton(MainUI)
        self.pushButtonHelp.setGeometry(QtCore.QRect(610,640,83,27))
        self.pushButtonHelp.setObjectName("pushButtonHelp")

        #self.pushButtonComplexQuery = QtGui.QPushButton(MainUI)
        #self.pushButtonComplexQuery.setGeometry(QtCore.QRect(140,640,102,27))
        #self.pushButtonComplexQuery.setObjectName("pushButtonComplexQuery")

        self.retranslateUi(MainUI)
        QtCore.QObject.connect(self.exitButton,QtCore.SIGNAL("clicked()"),MainUI.close)
        QtCore.QMetaObject.connectSlotsByName(MainUI)

    def retranslateUi(self, MainUI):
        MainUI.setWindowTitle(QtGui.QApplication.translate("MainUI", "SIB Explorer SPARQL", None, QtGui.QApplication.UnicodeUTF8))
        self.exitButton.setText(QtGui.QApplication.translate("MainUI", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.SPARQLButton.setText(QtGui.QApplication.translate("MainUI", "Query", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainUI", "SPARQL Query", None, QtGui.QApplication.UnicodeUTF8))
        #self.label_3.setText(QtGui.QApplication.translate("MainUI", "WQL Query Body", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonListAllAsTriples.setText(QtGui.QApplication.translate("MainUI", "List All (Triples)", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonListClassesOnly.setText(QtGui.QApplication.translate("MainUI", "List Classes Only", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonListPropertiesOnly.setText(QtGui.QApplication.translate("MainUI", "List Properties Only", None, QtGui.QApplication.UnicodeUTF8))
        #self.pushButtonQuery.setText(QtGui.QApplication.translate("MainUI", "Query...", None, QtGui.QApplication.UnicodeUTF8))
        #self.pushButtonCloseQueryWindows.setText(QtGui.QApplication.translate("MainUI", "Close All Query Windows", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonConnect.setText(QtGui.QApplication.translate("MainUI", "Connect", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonConnectionDetails.setText(QtGui.QApplication.translate("MainUI", "Connection Details", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidgetState.headerItem().setText(0,QtGui.QApplication.translate("MainUI", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonFullList.setText(QtGui.QApplication.translate("MainUI", "Full List by Class", None, QtGui.QApplication.UnicodeUTF8))
        #self.label_4.setText(QtGui.QApplication.translate("MainUI", "Common queries:", None, QtGui.QApplication.UnicodeUTF8))
        #self.pushButtonMakeTransaction.setText(QtGui.QApplication.translate("MainUI", "Make Transaction", None, QtGui.QApplication.UnicodeUTF8))
        #self.pushButtonSubscribe.setText(QtGui.QApplication.translate("MainUI", "Subscribe...", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonShowAsGraph.setText(QtGui.QApplication.translate("MainUI", "Show As Graph", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonHelp.setText(QtGui.QApplication.translate("MainUI", "Help!", None, QtGui.QApplication.UnicodeUTF8))
        #self.pushButtonComplexQuery.setText(QtGui.QApplication.translate("MainUI", "Complex Query", None, QtGui.QApplication.UnicodeUTF8))

