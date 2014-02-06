#!/usr/bin/env python

from Node import *
import sys
import uuid
import time
from RDFTransactionList import *
from TripleConvenienceFunctions import *

#all the rest of the functions
class PushBlob:
	def __init__(self):
		print("\nQuerying Home SmartSpace\n")

	def join(self):
		print "Joining..."
		self.nodename = str(uuid.uuid4())+"_queryHSS"
		self.theNode = ParticipantNode(self.nodename)

		self.theSmartSpace = self.theNode.discover()

		ans = self.theNode.join(self.theSmartSpace)

		print "*** Joined "+self.nodename+" with SmartSpace "+str(self.theSmartSpace)+" is "+str(ans)
	
	
		
	def showTriples(self):
		timeStartAll = time.time()

		print "\n\nRDF QUERY 0 - all things "
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.rdf_query(((None,None,None),"uri"))
		print resultLengthRDF(r)," results returned"
		print "Subjects=",subjectsRDF(r)
#		print "Objects=",objectsRDF(r)
		print "Predicates=",predicatesRDF(r)

	
		print "\n\nRDF QUERY 1 - all things of type MediaTrack"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.rdf_query(((None,"rdf:type","http://hss.nrc.nokia.com/mediaCDS#MediaTrack"),"uri"))
		print r
		print resultLengthRDF(r)," results returned"
		for i in r:

			r2 = q.rdf_query(((subjectRDF(i),"http://hss.nrc.nokia.com/mediaCDS#title",None),"literal"))
			title = objectRDF(r2[0])
			r3 = q.rdf_query(((subjectRDF(i),"http://hss.nrc.nokia.com/mediaCDS#artist",None),"literal"))
			artist = objectRDF(r3[0])
			print title,"by",artist

		print "\n\nRDF QUERY 2 - all things of type HomeMember"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.rdf_query(((None,"rdf:type","http://hss.nrc.nokia.com/hssuser#HomeMember"),"uri"))
		print r
		print "Subjects=",subjectsRDF(r)
		print "Objects=",objectsRDF(r)

		print "\n\nRDF QUERY 3 - all things of type FamilyMember"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.rdf_query(((None,"rdf:type","http://hss.nrc.nokia.com/hssuser#FamilyMember"),"uri"))
		print r
		print "Subjects=",subjectsRDF(r)
		print "Objects=",objectsRDF(r)

		print "\n\nWQL QUERY 0 - all things of type MediaTrack"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/mediaCDS#MediaTrack", False), "['inv', 'rdf:type']")
		print resultLengthWQL(r)," items"


		print "\n\nWQL QUERY 1 - all things of type HomeMember"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/hssuser#HomeMember", False), "['inv', 'rdf:type']")
		print r
		homemembers =  r

		print "\n\nWQL QUERY 2 - all things of type Visitor"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/hssuser#Visitor", False), "['inv', 'rdf:type']")
		print r
		visitors =  r

		print "\n\nWQL QUERY 3 - all things of type FamilyMember"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/hssuser#FamilyMember", False), "['inv', 'rdf:type']")
		print r
		familymembers = r

		print "Quick Summary of the HomeMember ontology"
		print resultLengthWQL(homemembers)," home members"
		print resultLengthWQL(visitors)," visitors"
		print resultLengthWQL(familymembers)," family members"

		print "\n\nWQL QUERY 4 - all albums"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/mediaCDS#MediaTrack", False), "['seq', ['inv', 'rdf:type'], 'http://hss.nrc.nokia.com/mediaCDS#album']")
		print r

		print "\n\nWQL QUERY 5 - all media objects "
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/mediaCDS#MediaObject", False), "['inv', 'rdf:type'] ")
		print r

		print "\n\nWQL QUERY 6 - all media objects with album as a filled property"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/mediaCDS#MediaObject", False), "['seq', ['inv', 'rdf:type'], 'http://hss.nrc.nokia.com/mediaCDS#album'] ")
		print r

		print "\n\nWQL QUERY 7 - all televisions"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/device#TV", False), "['inv', 'rdf:type'] ")
		print r

		print "\n\nWQL QUERY 8 - all devices"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/device#Device", False), "['inv', 'rdf:type'] ")
		print r

		print "\n\nNote the differences between WQL Query 9, WQL Query 10 and WQL Query 11"

		print "\n\nWQL QUERY 9 - all status of all things that are connected to a device"
		print " explanation: the query actually returns [ [] [] [] [] [on] [on] [off] ]  internally but returns a SET, ie [ [on] [off] ]"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/device#Device", False), "['seq', ['inv', 'rdf:type'], 'http://hss.nrc.nokia.com/device#connectedTo', 'http://hss.nrc.nokia.com/device#status']")
		print r

		print "\n\nWQL QUERY 10 - all status of all things that are connected to a device - mark 2"
		print " explanation: careful what you ask for"
		print "              for one of the devices is connected to two other devices BUT they are both ON, so if you read"
		print "              the actual print statement you'll notice that r2 is interally in the SIB [ [on] [on] ] and by"
		print "              the mathematics of a SET is just [ [on] ] which then means the print statement is actually"
		print "              misleading the reader..."
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/device#Device", False), "['inv', 'rdf:type']")
		for i in r:
			q2 = self.theNode.CreateQueryTransaction(self.theSmartSpace)
			r2 = q.wql_values_query(i,"['seq', 'http://hss.nrc.nokia.com/device#connectedTo', 'http://hss.nrc.nokia.com/device#status']")
			print i,"is connected to",resultLengthWQL(r2),"devices which amongst them have the statuses",r2
		
		print "\n\nWQL QUERY 11 - all status of all things that are connected to a device - mark 3"
		print " explanation: this is how it SHOULD be...everything taken one at a time which is what we really want"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/device#Device", False), "['inv', 'rdf:type']")
		for i in r:
			q2 = self.theNode.CreateQueryTransaction(self.theSmartSpace)
			r2 = q.wql_values_query(i,"['seq', 'http://hss.nrc.nokia.com/device#connectedTo']")
			for i2 in r2:
				q3 = self.theNode.CreateQueryTransaction(self.theSmartSpace)
				r3 = q.wql_values_query(i,"['seq', 'http://hss.nrc.nokia.com/device#status']")
				print i,"is connected to",r2,"devices which amongst them have the status",r3

		print "\n\nNow the same with a convenience function"

		print "\n\nWQL QUERY 12 - all status of all things that are connected to a device - mark 4"
		print " explanation: this is how it SHOULD be...with the added convenience of a convenience function"
		print "              and we're saving network connections and memory as a bonus because we're reusing the"
	        print "              query transaction...compare with WQL QUERY 13 which is QUERY 12 with the inefficiency of QUERY 11"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/device#Device", False), "['seq', ['inv', 'rdf:type']]")
		for i in r:
			r2 = q.wql_values_query(i,"['seq', 'http://hss.nrc.nokia.com/device#connectedTo']")
			for i2 in r2:
				r3 = q.wql_values_query(i2,"['seq', 'http://hss.nrc.nokia.com/device#status']")
				print i,"is connected to",r2,"devices which amongst them have the status",r3

		print "\n\nWQL QUERY 13 - all status of all things that are connected to a device - mark 5 (but not as good a Mark 4)"
		print " explanation: see the explanation in WQL QUERY 12"
		q1 = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		q2 = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		q3 = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q1.wql_values_query(("http://hss.nrc.nokia.com/device#Device", False), "['seq', ['inv', 'rdf:type']]")
		for i in r:
			r2 = q2.wql_values_query(i,"['seq', 'http://hss.nrc.nokia.com/device#connectedTo']")
			for i2 in r2:
				r3 = q3.wql_values_query(i2,"['seq', 'http://hss.nrc.nokia.com/device#status']")
				print i,"is connected to",r2,"devices which amongst them have the status",r3

		print "\n\nA little stress testing ... 10 queries, then I show the final tally of triples returned"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		totalTriples = 0
		timeStart = time.time()
		for i in range(0,10):
			if (i % 5) == 0: 
				print "."
			r = q.wql_values_query(("http://hss.nrc.nokia.com/device#Device", False), "['seq', ['inv', 'rdf:type']]")              
			totalTriples = totalTriples + resultLengthWQL(r)                                                                                            
			for i in r:
				r2 = q.wql_values_query(i,"['seq', 'http://hss.nrc.nokia.com/device#connectedTo']")
				totalTriples = totalTriples + resultLengthWQL(r2)
				for i2 in r2:
					r3 = q.wql_values_query(i2,"['seq', 'http://hss.nrc.nokia.com/device#status']")
					totalTriples = totalTriples + resultLengthWQL(r3)
		timeEnd = time.time()
		print "Total triples is",totalTriples,"in",timeEnd - timeStart,"s"




		print "\n\nWQL QUERY 14 - the set of all manufacturers in my house and the type of device"
		q = self.theNode.CreateQueryTransaction(self.theSmartSpace)
		r = q.wql_values_query(("http://hss.nrc.nokia.com/device#Device", False), "['seq', ['inv', 'rdf:type'], 'http://hss.nrc.nokia.com/device#manufacturer']")   
		print "There are",resultLengthWQL(r),"*distinct* device manufacturers recorded: ",r
		print " explanation: you can not navigate backwards from a literal, so the next query will result in no results"
                qr = []
		print r
		for i in r:
			r2 = q.wql_values_query(i,"['seq', ['inv', 'http://hss.nrc.nokia.com/device#manufacturer']]")
			qr.append(r2)
		print " ... ",len(qr),"results which are ",qr

		print " explanation: so again starting with each device (which is a uri), if there is a manufacturer then note the device type."
		print " Also note that the type of something also includes the super types"

		r = q.wql_values_query(("http://hss.nrc.nokia.com/device#Device", False), "['seq', ['inv', 'rdf:type']]")   
		for i in r:
			r2 = q.wql_values_query(i,"['seq', 'http://hss.nrc.nokia.com/device#manufacturer']")
			if resultLengthWQL(r2)!=0:
				r3 = q.wql_values_query(i,"['seq', 'rdf:type']")
				print "A device (",i,") made by ",r2," is a ",r3

		

		print "\n***********************"
		print "Total time elapsed was ",time.time()-timeStartAll,"s"	
		print "***********************"				





#the main function
if __name__ == "__main__":
	g = PushBlob()
	g.join()
	g.showTriples()
