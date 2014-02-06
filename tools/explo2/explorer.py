import sys
from PyQt4 import QtCore, QtGui
from Node import *
import uuid
import time
from explorer_ui import *
from connectDialog_ui import *
from wqlResult_ui import *
from makeTransaction_ui import *
from TripleConvenienceFunctions import *
from RDFTransactionList import *
import os

class MainUI(QtGui.QMainWindow):
    def __init__(self, ssd, parent=None):
        QtGui.QWidget.__init__(self, parent)
	self.smartSpaceData = ssd
        self.mainui = Ui_MainUI()
        self.mainui.setupUi(self)
        self.connectionDialog = ConnectionDialogUI(ssd)
	self.makeTransactionsDialog = MakeTransactionsDialogUI(ssd)
	self.wqlResultDialogs = []
	
	self.connect(self.mainui.pushButtonConnect,
                     QtCore.SIGNAL('clicked()'), 
                     self.connectButtonClicked )
	self.connect(self.mainui.pushButtonConnectionDetails,
                     QtCore.SIGNAL('clicked()'), 
                     self.showConnectionDetailsDialog )
        self.connect(self.mainui.pushButtonListAllAsTriples,
                     QtCore.SIGNAL('clicked()'), 
                     self.listAllAsTriples )
        self.connect(self.mainui.pushButtonListClassesOnly,
                     QtCore.SIGNAL('clicked()'), 
                     self.listClassesOnly )
        self.connect(self.mainui.pushButtonListPropertiesOnly,
                     QtCore.SIGNAL('clicked()'), 
                     self.listPropertiesOnly )
        self.connect(self.mainui.pushButtonFullList,
                     QtCore.SIGNAL('clicked()'), 
                     self.fullList )
        #self.connect(self.mainui.pushButtonQuery,
        #             QtCore.SIGNAL('clicked()'), 
        #             self.query )
        #self.connect(self.mainui.pushButtonSubscribe,
        #             QtCore.SIGNAL('clicked()'), 
        #             self.subscribe )
	self.connect(self.mainui.pushButtonCloseQueryWindows,
                     QtCore.SIGNAL('clicked()'), 
                     self.closeAllQueryWindows )
	#self.connect(self.mainui.pushButtonMakeTransaction,
        #             QtCore.SIGNAL('clicked()'), 
        #             self.makeTransactions )
	self.connect(self.mainui.pushButtonShowAsGraph,
                     QtCore.SIGNAL('clicked()'), 
                     self.showAsGraph )
	self.connect(self.mainui.pushButtonHelp,
                     QtCore.SIGNAL('clicked()'), 
                     self.showHelp )

	#self.mainui.comboCommon.addItems(["['inv', 'rdf:type']",
        #                                  "['seq'     ]",
        #                                  "['seq', ['inv', 'rdf:type'], 'owl:sameAs', 'rdf:type']"])
	#self.connect(self.mainui.comboCommon,
        #             QtCore.SIGNAL('activated(QString)'), 
        #             self.addCommonQuery )

        self.connect(self.mainui.SPARQLButton,
                     QtCore.SIGNAL('clicked()'), 
                     self.SPARQL_query )

	self.connectButtonClicked()

    def close(self):
	print "Bye."
	self.closeAllQueryWindows()
	sys.exit(0)

    def connectButtonClicked(self):
	self.connectionDialog.show()

    def showConnectionDetailsDialog(self):
	displayText="Space "+ssd.getSmartSpaceName()+" at "+ssd.getIPADDR()+":"+str(ssd.getPort())
	QtGui.QMessageBox.information(self,
                                      "Current Connection Details",
                                      displayText,
                                      QtGui.QMessageBox.Ok)

    def makeTransactions(self):
	self.makeTransactionsDialog.show()

    def listAllAsTriples(self):
        q = ssd.getNode().CreateQueryTransaction(ssd.getSmartSpace())
	r = q.rdf_query(((None,None,None),"uri"))
	QtGui.QMessageBox.information(self,"List All As Triples",
                                      str(len(r))+" results returned by rdf query(*, *, *)",
                                      QtGui.QMessageBox.Ok)
	self.mainui.treeWidgetState.clear()
	self.mainui.treeWidgetState.setColumnCount(4)
	self.mainui.treeWidgetState.setColumnWidth(0, 300)
	self.mainui.treeWidgetState.setColumnWidth(1, 300)
	self.mainui.treeWidgetState.setColumnWidth(2, 300)
	self.mainui.treeWidgetState.setColumnWidth(3, 50)
	self.mainui.treeWidgetState.setColumnWidth(4, 200)
	self.mainui.treeWidgetState.setHeaderLabels(["Subject", "Predicate", "Object", "Literal?"])
        print "ListAllAsTriples: got", r
	for i in r:
		item = QtGui.QTreeWidgetItem()
		item.setText(0, str(subjectRDF(i)))
		item.setText(1, str(predicateRDF(i)))
		item.setText(2, str(objectRDF(i)))
		item.setText(3, str(tripleObjectType(i)))

		item.setTextColor(0,QtGui.QColor(0,0,0))
		item.setTextColor(1,QtGui.QColor(0,0,0))
		item.setTextColor(2,QtGui.QColor(0,0,0))
		item.setTextColor(3,QtGui.QColor(0,128,0))
                print "ListAllAsTriples: triple ", i, "is literal?", tripleObjectType(i)
		if tripleObjectType(i)==True:
			item.setTextColor(2,QtGui.QColor(32,0,255))

		self.mainui.treeWidgetState.addTopLevelItem(item)

    def listClassesOnly(self):
        q = ssd.getNode().CreateQueryTransaction(ssd.getSmartSpace())
	#r = q.wql_values_query(("rdfs:Class", False), ['inv', 'rdf:type'])
        r=q.sparql_query("SELECT ?a WHERE {?a ?b <http://www.w3.org/2000/01/rdf-schema#Class>}")
        if r==[]:
           r=q.sparql_query("SELECT ?a WHERE {?a ?b <rdfs:Class>}")      
	QtGui.QMessageBox.information(self,
                                      "List All As Classes",
                                      "%s results returned by SPARQL query rdfs:Class"%str(len(r)),
                                      QtGui.QMessageBox.Ok)
	self.mainui.treeWidgetState.clear()
	self.mainui.treeWidgetState.setColumnCount(1)
	self.mainui.treeWidgetState.setHeaderLabels(["Class"])

	for i in r:
		item = QtGui.QTreeWidgetItem()
		item.setText(0,str(i[0][2]))
		self.mainui.treeWidgetState.addTopLevelItem(item)


    def listPropertiesOnly(self):
        q = ssd.getNode().CreateQueryTransaction(ssd.getSmartSpace())
	#r = q.wql_values_query(("rdf:Property", False), ['inv', 'rdf:type'])
        r=q.sparql_query("SELECT ?a WHERE {?a ?b <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>}")
	QtGui.QMessageBox.information(self,
                                      "List All Properties",
                                      "%s results returned by SPARQL query rdf:Property"%str(len(r)),
                                      QtGui.QMessageBox.Ok)
	self.mainui.treeWidgetState.clear()
	self.mainui.treeWidgetState.setColumnCount(1)
	self.mainui.treeWidgetState.setHeaderLabels(["Property"])
	for i in r:
		item = QtGui.QTreeWidgetItem()
		item.setText(0,str(i[0][2]))
		self.mainui.treeWidgetState.addTopLevelItem(item)	

    def fullList(self):
        q = ssd.getNode().CreateQueryTransaction(ssd.getSmartSpace())
	#r_classes = q.wql_values_query(("rdfs:Class", False), ['inv', 'rdf:type'])
        r_classes=q.sparql_query("SELECT ?a WHERE {?a ?b <http://www.w3.org/2000/01/rdf-schema#Class>}")
        if r_classes==[]: 
           r_classes=q.sparql_query("SELECT ?a WHERE {?a ?b <rdfs:Class>}") 
	#r_properties = set(q.wql_values_query(("rdf:Property", False), 
        #                                      "['inv', 'rdf:type']", False))
        r_prop=q.sparql_query("SELECT ?a WHERE {?a ?b <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>}")
        r_propert=[]
        for app in r_prop:
           r_propert.append(app[0][2])  
        r_properties=set(r_propert)
        # For full list, the type property is superfluous as the view shows
        # that clearly anyway --jho
        r_properties -= set(["http://www.w3.org/1999/02/22-rdf-syntax-ns#type"])
        
        
#	QtGui.QMessageBox.information(self,"Full List","Generating",QtGui.QMessageBox.Ok)
	self.mainui.treeWidgetState.clear()
	self.mainui.treeWidgetState.setIndentation(35)
	self.mainui.treeWidgetState.setColumnCount(2)
	self.mainui.treeWidgetState.setColumnWidth(0, 500)
	self.mainui.treeWidgetState.setColumnWidth(1, 10000)
	self.mainui.treeWidgetState.setHeaderLabels(["Class/Instance/Property", 
                                                     "Value"])
	#for each class
	
	items=[]
	queries=2  #note the two previous queries above!
	print "Starting full list ", len(r_classes), " classes"
	for i in r_classes:
		wi = QtGui.QTreeWidgetItem()
		wi.setText(0, str(i[0][2]))
		wi.setTextColor(0, QtGui.QColor(0, 0, 255))
		wi.setExpanded(False)
		wi.setFirstColumnSpanned(True)		
		#r2_instances = q.wql_values_query(i, "['inv', 'rdf:type']")
                r2_instances=q.sparql_query("SELECT ?a WHERE {?a ?b <"+str(i[0][2])+">"+"}")
		queries = queries + 1
		print "...  ", len(r2_instances), " instances"
		for i2 in r2_instances:
			wi2 = QtGui.QTreeWidgetItem()
			wi2.setText(0, str(i2[0][2]))
			wi2.setTextColor(0, QtGui.QColor(255,0,64))
			wi.addChild(wi2)
                        print "FULL_LIST: querying properties for node", i2[0][2]
                        #i_values = q.rdf_query(((i2[0][2], None, None), 'literal'))
                        i_values=q.sparql_query("SELECT ?a ?b ?c WHERE {<"+str(i2[0][2])+">"+" ?b ?c}") 
                        print "FULL_LIST: property triples:", i_values
                        queries = queries + 1
                        checked_values = []
                        for v in i_values:
                            if  v[1][2] in r_properties: #predicateRDF(v) in r_properties:
                                checked_values.append(v[2][2])   #objectRDF(v))
                                wi3 =  QtGui.QTreeWidgetItem()
                                wi3.setText(0,str(v[1][2]))   #predicateRDF(v)))
                                wi3.setText(1,str(v[2][2]))   #objectRDF(v)))
                                wi3.setTextColor(0,QtGui.QColor(0,0,0))
                                wi3.setTextColor(1,QtGui.QColor(0,0,0))
                                wi2.addChild(wi3)
		items.append(wi)

		
	self.mainui.treeWidgetState.insertTopLevelItems(0,items)
	QtGui.QMessageBox.information(self, 
                                      "Full List", 
                                      str(queries) + " queries performed",
                                      QtGui.QMessageBox.Ok)

    def query(self):
	w = WQLResultUI(self.mainui.lineEditWQLFrame,
                        self.mainui.lineEditWQLBody,
                        self.smartSpaceData)
	w.show()
	self.wqlResultDialogs.append(w)

    #def subscribe(self):
    #	w = WQLResultUIsubscription(self.mainui.lineEditWQLFrame,
    #                                self.mainui.lineEditWQLBody,
    #                                self.smartSpaceData)
    #	w.show()
    #	self.wqlResultDialogs.append(w)

    def insert(self):
        i = MakeTransactionsDialogUI(self.smartSpaceData)
        i.show()
	
    def addCommonQuery(self,s):
	self.mainui.lineEditWQLBody.setText(s)

    def closeAllQueryWindows(self):
    	for w in self.wqlResultDialogs:
    		w.hide()
    	self.wqlResultDialogs=[]

    def uriColour(self,p):
	colour = "black"

	if "www.w3.org/1999/02/22-rdf-syntax-ns" in p:
		colour = "cyan"
	if  "www.nokia.com" in  p:
		colour = "green"
	if  "www.w3.org/2002/07/owl" in  p:
		colour = "red"
	return "fontcolor="+colour+",color="+colour

    def showAsGraph(self):
	q = ssd.getNode().CreateQueryTransaction(ssd.getSmartSpace())
	r_triples = q.rdf_query(((None, None, None),"uri"))
	dot = ""
	for t in r_triples:
		subj = subjectRDF(t)
		pred = predicateRDF(t)
		obj = objectRDF(t)
		
		dot = dot + "\042"+subj+"\042 [ fontsize=9,shape=box,"+self.uriColour(subj)+" ];\n"
		dot = dot + "\042"+obj+"\042 [ fontsize=9,shape=box,"+self.uriColour(obj)+" ];\n"
		dot = dot + "\042"+subj+"\042 -> \042"+obj+"\042  [ fontsize=8,"+self.uriColour(pred)+",label=\042"+pred+"\042 ]  ;\n"	
			
	dotheader = "digraph \042RDF\042 {\nrankdir=BT;\n"
	dotfooter = "}"
	dotoutput = dotheader + dot + dotfooter
	f = open('/tmp/rdf.dot','w')
	f.write(dotoutput)
	f.close()
	msg="Attempting to start dotty - assuming GraphViz is installed and dotty is on the PATH\n"
	msg=msg+"If this fails run dotty manually. The graph is written to /tmp/rdf.dot\n"
	msg=msg+"Alternativly process rdf.dot using GraphViz's dot command\n"
	msg=msg+"Graph contains "+str(len(r_triples))+" elements"
	QtGui.QMessageBox.information(self,"Show As Graph",msg,QtGui.QMessageBox.Ok)
	os.system("dotty /tmp/rdf.dot &")

    def showHelp(self):
	msg = "(C)2008 Nokia Corporation\n"
	msg=msg+"No warranty etc etc...use at own risk etc etc\n\n"
	msg=msg+"Good news...this is the help\n"
	msg=msg+"Bad news...this is all the help...sorry\n"
	QtGui.QMessageBox.information(self,"Help",msg,QtGui.QMessageBox.Ok)
    
    def SPARQL_query(self):
        q = ssd.getNode().CreateQueryTransaction(ssd.getSmartSpace())
        triple=q.sparql_query(str(self.mainui.lineSPARQL.text()))
        QtGui.QMessageBox.information(self,"SPARQL query",
                                      str(len(triple))+" results returned by SPARQL query",
                                      QtGui.QMessageBox.Ok)
        self.mainui.treeWidgetState.clear()
	self.mainui.treeWidgetState.setColumnCount(len(triple[0])*2)
        for i in range(len(triple[0])*2):
           item = QtGui.QTreeWidgetItem()
           if (i%2):
             self.mainui.treeWidgetState.setColumnWidth(i,200/len(triple[0]))
             label.append("type")
           else:
	     self.mainui.treeWidgetState.setColumnWidth(i,800/len(triple[0]))
             if i==0:
                label=[str(triple[0][i][0])]
             else:
                label.append(str(triple[0][i/2][0]))
	self.mainui.treeWidgetState.setHeaderLabels(label)
        print "Triples: got"
        for el in  triple:
           print el
	for i in triple:
          item = QtGui.QTreeWidgetItem()
          for j in range(len(triple[0])*2):
             if (j%2):
                item.setText(j, str(i[j/2][1]))
                item.setTextColor(j,QtGui.QColor(32,0,255))
             else:
		item.setText(j, str(i[j/2][2]))
                item.setTextColor(j,QtGui.QColor(0,0,0))

             self.mainui.treeWidgetState.addTopLevelItem(item)
        

class MakeTransactionsDialogUI(QtGui.QMainWindow):
    def __init__(self, ssd, parent=None):
        QtGui.QWidget.__init__(self, parent)
	self.trans = RDFTransactionList()
        self.smartSpaceData = ssd
        self.makeTransactionDialogUi = Ui_DialogMakeTransaction()
        self.makeTransactionDialogUi.setupUi(self)
	self.connect(self.makeTransactionDialogUi.pushButtonGenUUID4Subject,
                     QtCore.SIGNAL('clicked()'), 
                     self.genUUID4subject )
	self.connect(self.makeTransactionDialogUi.pushButtonPopulate,
                     QtCore.SIGNAL('clicked()'), 
                     self.populateComboBoxesWithURIs )
	self.connect(self.makeTransactionDialogUi.pushButtonPopulateNS,
                     QtCore.SIGNAL('clicked()'), 
                     self.populateComboBoxesWithNSs )
	self.connect(self.makeTransactionDialogUi.pushButtonAdd,
                     QtCore.SIGNAL('clicked()'), 
                     self.add )

    def reject(self):
	self.hide()

    def genUUID4subject(self):
	u=str(uuid.uuid4())
	self.makeTransactionDialogUi.lineEditSubject.setText(u)

    def add(self):
	#the rule is,:
	#if ns box is checked then prepend the nsuri combo box to the user entered data with a #
	subNS = str(self.makeTransactionDialogUi.comboBoxSubjectNS.currentText())
	preNS = str(self.makeTransactionDialogUi.comboBoxPredicateNS.currentText())
	objNS = str(self.makeTransactionDialogUi.comboBoxObjectNS.currentText())

	subU  = str(self.makeTransactionDialogUi.lineEditSubject.text())
	preU  = str(self.makeTransactionDialogUi.lineEditPredicate.text())
	objU  = str(self.makeTransactionDialogUi.lineEditObject.text())

	#0 = not checked, 2=checked,    1 is for tristate boxes which we do not use
	subC  = self.makeTransactionDialogUi.checkBoxSubjectUse.checkState()
	preC  = self.makeTransactionDialogUi.checkBoxPredicateUse.checkState()
	objC  = self.makeTransactionDialogUi.checkBoxObjectUse.checkState()

	#true if checked, False otherwise - these belong to the same parent widget so they're
 	#guaranteed to be mutually exclusive....hopefully QT4 got it right ;-)
	olit = self.makeTransactionDialogUi.radioButtonLiteral.isChecked()
	ouri = self.makeTransactionDialogUi.radioButtonLiteral.isChecked()  

	print "+->",olit,subNS,subU,subC

	transSubject = subU
	transPredicate = preU
	transObject = objU
	if subC==2:
		transSubject = subNS + "#" + transSubject
	if preC==2:
		transPredicate = preNS + "#" + transPredicate
	if objC==2:
		transObject = objNS + "#" + transObject

	print "-->", transSubject, transPredicate, transObject

	if olit==True:
		self.trans.add_literal(transSubject, 
                                       transPredicate, 
                                       transObject)
	else:
		self.trans.add_uri(transSubject,
                                   transPredicate,
                                   transObject)

	self.updateList()

    def updateList(self):
	self.makeTransactionDialogUi.listWidgetTriples.setColumnCount(4)
	self.makeTransactionDialogUi.listWidgetTriples.clear()
	tablerow=1
	for i in self.trans.get():
		lws = QtGui.QTableWidgetItem()
		lwp = QtGui.QTableWidgetItem()
		lwo = QtGui.QTableWidgetItem()
		lwot = QtGui.QTableWidgetItem()

		lws.setText(i[0][0])
		lws.setTextColor(QtGui.QColor(0, 0, 0))
		lwp.setText(i[0][1])
		lwp.setTextColor(QtGui.QColor(0, 0, 0))
		lwo.setText(i[0][2])
		lwo.setTextColor(QtGui.QColor(0, 0, 0))
		lwot.setText(i[1])
		lwot.setTextColor(QtGui.QColor(0, 128, 0))

		if i[1]=="literal":
			lwo.setTextColor(QtGui.QColor(32, 0, 255))

		print tablerow
		self.makeTransactionDialogUi.listWidgetTriples.setItem(tablerow,0,lws)
		self.makeTransactionDialogUi.listWidgetTriples.setItem(tablerow,1,lwp)
		self.makeTransactionDialogUi.listWidgetTriples.setItem(tablerow,2,lwo)
		self.makeTransactionDialogUi.listWidgetTriples.setItem(tablerow,3,lwot)

		tablerow = tablerow + 1

    def populateComboBoxesWithNSs(self):
	q = self.smartSpaceData.getNode().CreateQueryTransaction(self.smartSpaceData.getSmartSpace())
	r_properties = q.wql_values_query(("rdf:Property", False),"['inv', 'rdf:type']")
	r_allUris= subjectsRDF(q.rdf_query(((None, None, None), "uri")))
	r_namespaces = self.extractNamespaces(r_allUris + r_properties)

	for i in r_properties:
		self.makeTransactionDialogUi.comboBoxPredicateNS.addItem(i)
	
	for i in r_namespaces:
		self.makeTransactionDialogUi.comboBoxSubjectNS.addItem(i)
		self.makeTransactionDialogUi.comboBoxObjectNS.addItem(i)
		self.makeTransactionDialogUi.comboBoxPredicateNS.addItem(i)

    def populateComboBoxesWithURIs(self):
	q = self.smartSpaceData.getNode().CreateQueryTransaction(self.smartSpaceData.getSmartSpace())
	r_properties = q.wql_values_query(("rdf:Property", False), "['inv', 'rdf:type']")
	r_allUris= subjectsRDF(q.rdf_query(((None, None, None), "uri")))
	r_namespaces = self.extractNamespaces(r_allUris+r_properties)

	for i in r_properties:
		self.makeTransactionDialogUi.comboBoxPredicateNS.addItem(i)

	for i in r_allUris:
		self.makeTransactionDialogUi.comboBoxSubjectNS.addItem(i)
		self.makeTransactionDialogUi.comboBoxObjectNS.addItem(i)
	
	for i in r_namespaces:
		self.makeTransactionDialogUi.comboBoxSubjectNS.addItem(i)
		self.makeTransactionDialogUi.comboBoxObjectNS.addItem(i)
		self.makeTransactionDialogUi.comboBoxPredicateNS.addItem(i)
	

    def extractNamespaces(self,ls):
	print ls
	ns = []
	for i in ls:
		istr = str(i)
		if "#" in istr:
			n = istr.split("#")
			if n not in ns:
				ns.append(n[0])
	return ns
		

		
	
class ConnectionDialogUI(QtGui.QMainWindow):
    def __init__(self, ssd, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.smartSpaceData = ssd
        self.connectionDialogui = Ui_DialogConnect()
        self.connectionDialogui.setupUi(self)
	self.populateComboBox()
	self.connect(self.connectionDialogui.comboBoxPredef, 
                     QtCore.SIGNAL('activated(QString)'), 
                     self.autoComplete )


    def accept(self):
	print "accept"
	ssd.setSmartSpaceName(self.connectionDialogui.lineEditSSName.text())
	ssd.setIPADDR(self.connectionDialogui.lineEditIPAddr.text())
	ssd.setPort(self.connectionDialogui.lineEditPort.text())
	ans = ssd.joinSpace()
	if ans == True:
		QtGui.QMessageBox.information(self,
                                              "Explorer",
                                              "Connection Succesful",
                                              QtGui.QMessageBox.Ok)

		cbstr="'"+self.connectionDialogui.lineEditSSName.text()+"','"+self.connectionDialogui.lineEditIPAddr.text()+"','"+self.connectionDialogui.lineEditPort.text()+"'"
		self.connectionDialogui.comboBoxPredef.addItem(cbstr)
	else:
		QtGui.QMessageBox.critical(self,
                                           "Explorer",
                                           "Connection Failed",
                                           QtGui.QMessageBox.Ok)
	self.hide()

    def reject(self):
	self.hide()

    def populateComboBox(self):
	servers=[]
	servers.append("'x', '127.0.0.1', '10010'")
        servers.append("'X', '127.0.0.1', '10010'")

	self.connectionDialogui.comboBoxPredef.addItems(servers)

    def autoComplete(self,s):
	sl = eval(str(s))
	self.connectionDialogui.lineEditSSName.setText(sl[0])
	self.connectionDialogui.lineEditIPAddr.setText(sl[1])
	self.connectionDialogui.lineEditPort.setText(sl[2])



class WQLResultUI(QtGui.QMainWindow):
	def __init__(self, wqlf,wqlb,ssd, parent=None):
		print "initialised query results dialog"
        	QtGui.QWidget.__init__(self, parent)
		self.smartSpaceData = ssd
		self.wqlResultUI = Ui_WQLResultDialog()
		self.wqlResultUI.setupUi(self)
		self.wqlframe=wqlf
		self.wqlbody=wqlb
		self.performQuery()

	def performQuery(self):
		print "performing query"
		q = self.smartSpaceData.getNode().CreateQueryTransaction(self.smartSpaceData.getSmartSpace())
		print "making query"
		r = q.wql_values_query((str(self.wqlframe.text()), False), str(self.wqlbody.text()))
		print "Clearing list box"
		self.wqlResultUI.listWidgetResults.clear()
		print "parsing results with ",len(r),"results returned"
		for i in r:
			lw = QtGui.QListWidgetItem()
			lw.setText(str(i))
			self.wqlResultUI.listWidgetResults.addItem(lw)
		print "writing additional information to label fields"
		self.wqlResultUI.labelQuery.setText(self.wqlframe.text()+" |\n   "+self.wqlbody.text())
		self.wqlResultUI.labelResults.setText("Query result set contains "+str(len(r))+" elements")


			
	def reject(self):
		self.hide()


class WQLResultUIsubscription(WQLResultUI):
	def __init__(self, wqlf,wqlb,ssd, parent=None):
		print "initialised subscriptioin results dialog"
        	QtGui.QWidget.__init__(self, parent)
		self.smartSpaceData = ssd
		self.wqlResultUI = Ui_WQLResultDialog()
		self.wqlResultUI.setupUi(self)
		self.wqlframe=wqlf
		self.wqlbody=wqlb
		q = self.smartSpaceData.getNode().CreateSubscribeTransaction(self.smartSpaceData.getSmartSpace())
		q.subscribe_wql(str(self.wqlframe.text()),str(self.wqlbody.text()),self)
		self.wqlResultUI.labelQuery.setText(self.wqlframe.text()+" |\n   "+self.wqlbody.text())
		self.wqlResultUI.labelResults.setText("Subscribing and waiting for results")

	def handle(self,nodelist):		
		print "Clearing list box"
		self.wqlResultUI.listWidgetResults.clear()
		print "parsing results with ",len(nodelist),"results returned"
		for i in nodelist:
			lw = QtGui.QListWidgetItem()
			lw.setText(str(i))
			self.wqlResultUI.listWidgetResults.addItem(lw)
		print "writing additional information to label fields"

		self.wqlResultUI.labelResults.setText("Subscription result set contains "+str(len(nodelist))+" elements")

			
	def reject(self):
		self.hide()



class SmartSpaceData:
    def __init__(self):
	self.SmartSpaceName = "undefined"
	self.IPADDR = "no connection"
	self.Port = 0
	self.nodename = str(uuid.uuid4())+"_sibexplorer1.0"
	self.theNode = ParticipantNode(self.nodename)
	self.theSmartSpace = "" 

    def setParameters(self,n,i,p):
	self.SmartSpaceName = n
	self.IPADDR = i
	self.Port = p

    def getSmartSpaceName(self):
	return self.SmartSpaceName

    def getIPADDR(self):
	return self.IPADDR

    def getPort(self):
	return self.Port

    def getNode(self):
	print self.theNode
	return self.theNode

    def getSmartSpace(self):
	return self.theSmartSpace

    def setSmartSpaceName(self,n):
	self.SmartSpaceName = str(n)

    def setIPADDR(self,i):
	self.IPADDR = str(i)

    def setPort(self,p):
	self.Port = int(p)

    def joinSpace(self):
#	print "joining space ",(self.IPADDR,self.Port),self.SmartSpaceName
	self.theSmartSpace = ( self.SmartSpaceName, (TCPConnector, (self.IPADDR,self.Port)  ))
	ans = self.theNode.join(self.theSmartSpace)
#	print "*** Joined "+self.nodename+" with SmartSpace "+str(self.theSmartSpace)+" is "+str(ans)
#	print "result=",ans
	return ans



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ssd = SmartSpaceData()
    mainapp = MainUI(ssd)

    mainapp.show()
    sys.exit(app.exec_())
