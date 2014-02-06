#!/usr/bin/python

from sib.SIBLib import * 

node1 = SibLib("127.0.0.1", 10010, "test_insert")
node1.join_sib()

query = """SELECT ?subject WHERE { ?subject rdfs:subClassOf ns:Box}"""

result = node1.execute_query(query)

node1.leave_sib()

print result
