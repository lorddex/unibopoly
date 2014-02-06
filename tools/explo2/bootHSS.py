#!/usr/bin/env python

from Node import *
import sys
import uuid
import time
from  binascii import *
from RDFTransactionList import *

#all the rest of the functions
class PushBlob:
	def __init__(self):
		print("\nBooting Home SmartSpace\n")

	def join(self):
		print "Joining..."
		self.nodename = str(uuid.uuid4()) + "_bootHSS"
		self.theNode = ParticipantNode(self.nodename)
		self.theSmartSpace = self.theNode.discover()

		ans = self.theNode.join(self.theSmartSpace)

		print "*** Joined " + self.nodename + " with SmartSpace " + str(self.theSmartSpace) + " is " + str(ans)
	
	def createOntologicalStructures(self):
		t = RDFTransactionList()
		ns="http://hss.nrc.nokia.com/hssuser#"
		t.add_subClass(ns + "FamilyMember", ns + "HomeMember")
		t.add_subClass(ns + "Visitor", ns + "HomeMember")
		p1 = self.theNode.CreateInsertTransaction(self.theSmartSpace)
		p1.send( t.get() )
	
		t = RDFTransactionList()
		ns="http://hss.nrc.nokia.com/mediaCDS#"
		t.add_subClass(ns + "MediaTrack", ns + "MediaItem")
		t.add_subClass(ns + "MediaItem", ns + "MediaObject")
		p1.send( t.get() )
	
		t = RDFTransactionList()
		ns="http://hss.nrc.nokia.com/device#"
		t.add_subClass(ns + "TV", ns + "Device")
		t.add_subClass(ns + "Radio", ns + "Device")
		t.add_subClass(ns + "CDPlayer", ns + "Device")
		t.add_subClass(ns + "DVDPlayer", ns + "Device")
		t.add_subClass(ns + "ExternalSpeaker", ns + "Device")
		p1.send( t.get() )	
		self.theNode.CloseInsertTransaction(p1)

	def createUsers(self):
		t = RDFTransactionList()
		ns="http://hss.nrc.nokia.com/hssuser#"

		u1 = ns + str(uuid.uuid4())
		u2 = ns + str(uuid.uuid4())
		u3 = ns + str(uuid.uuid4())
		u4 = ns + str(uuid.uuid4())
		u5 = ns + str(uuid.uuid4())

		t.setType(u1, ns + "FamilyMember")
		t.setType(u2, ns + "FamilyMember")
		t.setType(u3, ns + "FamilyMember")
		t.setType(u4, ns + "Visitor")
		t.setType(u5, ns + "Visitor")

		t.add_literal(u1, ns + "name", "Ian")
		t.add_literal(u2, ns + "name", "Pekka")
		t.add_literal(u3, ns + "name", "Olli")
		t.add_literal(u4, ns + "name", "Jukka")
		t.add_literal(u5, ns + "name", "Seamus")

		p1 = self.theNode.CreateInsertTransaction(self.theSmartSpace)
		p1.send( t.get() )
		self.theNode.CloseInsertTransaction(p1)


	def createMediaEntries(self):
		t = RDFTransactionList()
		ns="http://hss.nrc.nokia.com/mediaCDS#"

		u1 = ns + str(uuid.uuid4())
		u2 = ns + str(uuid.uuid4())
		u3 = ns + str(uuid.uuid4())
		u4 = ns + str(uuid.uuid4())

		t.setType(u1, ns + "MediaTrack")
		print "**", ns + "MediaTrack"
		t.add_literal(u1, ns + "artist", "Peter Gabriel")		
		t.add_literal(u1, ns + "album", "Hit")
		t.add_literal(u1, ns + "genre", "Progessive")				
		t.add_literal(u1, ns + "title", "Solsbury Hill")				

		t.setType(u2, ns + "MediaTrack")
		t.add_literal(u2, ns + "artist", "Rush")		
		t.add_literal(u2, ns + "album", "2112")
		t.add_literal(u2, ns + "genre", "Progessive")				
		t.add_literal(u2, ns + "title", "Passage to Bangkok")				

		t.setType(u3, ns + "MediaTrack")
		t.add_literal(u3, ns + "artist", "Genesis")		
		t.add_literal(u3, ns + "album", "Lamb Lies Down")
		t.add_literal(u3, ns + "genre", "Progessive")				
		t.add_literal(u3, ns + "title", "Lamb Lies Down on Broadway")

		t.setType(u4, ns + "MediaTrack")
		t.add_literal(u4, ns + "artist", "Jaco Pastorius")		
		t.add_literal(u4, ns + "album", "Jazo Pastorius")
		t.add_literal(u4, ns + "genre", "Jazz")				
		t.add_literal(u4, ns + "title", "Portrait of Tracy")

		p1 = self.theNode.CreateInsertTransaction(self.theSmartSpace)
		p1.send( t.get() )
		self.theNode.CloseInsertTransaction(p1)
		
	def createDevices(self):
		t = RDFTransactionList()
		ns="http://hss.nrc.nokia.com/device#"
		
		u1 = ns + str(uuid.uuid4())
		u2 = ns + str(uuid.uuid4())
		u3 = ns + str(uuid.uuid4())
		u4 = ns + str(uuid.uuid4())	
		u5 = ns + str(uuid.uuid4())
		u6 = ns + str(uuid.uuid4())
		u7 = ns + str(uuid.uuid4())
		u8 = ns + str(uuid.uuid4())	

		t.setType(u1, ns + "TV")
		t.setType(u2, ns + "TV")
		t.setType(u3, ns + "Radio")
		t.setType(u4, ns + "Radio")	
		t.setType(u5, ns + "CDPlayer")
		t.setType(u6, ns + "DVDPlayer")
		t.setType(u7, ns + "ExternalSpeaker")
		t.setType(u8, ns + "ExternalSpeaker")

		t.add_uri(u6, ns + "connectedTo", u2)
		t.add_uri(u5, ns + "connectedTo", u7)
		t.add_uri(u5, ns + "connectedTo", u8)

		t.add_literal(u1, ns + "status", "StandBy")
		t.add_literal(u2, ns + "status", "Off")
		t.add_literal(u3, ns + "status", "On")
		t.add_literal(u4, ns + "status", "Off")
		t.add_literal(u5, ns + "status", "On")
		t.add_literal(u6, ns + "status", "Off")
		t.add_literal(u7, ns + "status", "On")
		t.add_literal(u8, ns + "status", "On")

		t.add_literal(u1, ns + "manufacturer", "Nokia")
		t.add_literal(u2, ns + "manufacturer", "Sony")
		t.add_literal(u3, ns + "manufacturer", "Sony")
		t.add_literal(u4, ns + "manufacturer", "Toshiba")
		t.add_literal(u5, ns + "manufacturer", "Toshiba")
		t.add_literal(u6, ns + "manufacturer", "Sanyo")
		t.add_literal(u7, ns + "manufacturer", "Bose")
		t.add_literal(u8, ns + "manufacturer", "Genelec")	

		p1 = self.theNode.CreateInsertTransaction(self.theSmartSpace)
		p1.send( t.get() )
		self.theNode.CloseInsertTransaction(p1)


	def createUnificationExample(self):
		t = RDFTransactionList()

		ns = "http://donkey.eeor.disney.com/animals#"
		u1 = ns + str(uuid.uuid4())
		t.setType(u1, ns + "Donkey")
		t.add_literal(u1, ns + "petname", "Dobbin")
	
		ns="http://www.nokia.com/persons#"
		u2 = ns + str(uuid.uuid4())
		t.setType(u2, ns + "Person")
		t.add_literal(u2, ns + "number", "42")
		t.add_literal(u2, ns + "name", "Flash Gordon")

		t.unify(u1, u2)

		p1 = self.theNode.CreateInsertTransaction(self.theSmartSpace)
		p1.send( t.get() )
		self.theNode.CloseInsertTransaction(p1)
	


#the main function
if __name__ == "__main__":
	g = PushBlob()
	g.join()
	g.createOntologicalStructures()
	g.createUsers()
	g.createMediaEntries()
	g.createDevices()
	g.createUnificationExample()
	

