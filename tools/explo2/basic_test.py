import Node
import time
import sys

# Create a node instance
# One can also subclass ParticipantNode
# Constructor argument: String representing node id
# Node id can be anything, not restricted by the system

node = Node.ParticipantNode("SIB Tester")
# ss_handle = node.discover(method = "mDNS")
ss_handle = node.discover()
print ss_handle

if not node.join(ss_handle):
    sys.exit('Could not join to Smart Space')

print "--- Member of SS:", node.member_of

class RdfMsgHandler:
    def handle(self, added, removed):
        print "Subscription:"
        for i in added:
            print "Added:", str(i)
        for i in removed:
            print "Removed:", str(i)

class NodeMsgHandler:
    def handle(self, added, removed):
        print "Subscription:"
        for i in added:
            print "Added: x1 drinks", str(i)
        for i in removed:
            print "Removed: x1 drinks", str(i)

# Create a proactive (sending) session with the
# smart space


# Put information to smart space using the session
# created earlier
# Parameters: string containing the information
#             string containing the information type
# Information and type can be any string, they are
# not restricted by the system

init_triples = [(("x1", "rdf:type", "person"), "uri", "uri"),
                (("x1", "lives", "Espoo"), "uri", "literal"),
                (("x1", "name", "Timo"), "uri", "literal"),
                (("x1", "knows", "x2"), "uri", "uri"),
                (("x2", "rdf:type", "person"), "uri", "uri"), 
                (("x2", "lives", "Espoo"), "uri", "literal"),
                (("x2", "name", "Risto"), "uri", "literal"),
                (("person","rdfs:subClassOf","thing"), "uri", "uri"),
                (("_:foo", "rdf:type", "person"), "uri", "uri")]
insert = [(("x1", "drinks", "beer"), "uri", "literal")]
update_rem = [(("x1", "drinks", "beer"), "uri", "literal")]
update_ins = [(("x1", "drinks", "wine"), "uri", "literal")]


rs1 = node.CreateSubscribeTransaction(ss_handle)
result_rdf = rs1.subscribe_rdf([((None, 'lives', None), 'literal')], RdfMsgHandler())

rs2 = node.CreateSubscribeTransaction(ss_handle)
result_wql = rs2.subscribe_wql_values(('x1', False), ['seq', 'drinks'], NodeMsgHandler(), True)
print "RDF Subscribe initial result:", result_rdf
print "WQL values subscribe initial result:", result_wql
pro = node.CreateInsertTransaction(ss_handle)

pro.send(init_triples, confirm = True)
pro.send(insert, confirm = True)
node.CloseInsertTransaction(pro)

upd = node.CreateUpdateTransaction(ss_handle)
upd.update(update_ins, "RDF-M3", update_rem, "RDF-M3", confirm = True)
node.CloseUpdateTransaction(upd)

#print "Querying: (*, lives, *)"
#qs = node.CreateQuerySession(ss_handle)
#print "--- Connections", node.connections
#result = qs.query("",(None, "lives", None),"TRIPLE")
#node.CloseQuerySession(qs)
#for item in result:
#    type, triple, ts = item
#    print "Got triple: ", triple, ", stored at", str(ts)
#print "--- Connections", node.connections


print "Querying what is being drunk"
qs = node.CreateQueryTransaction(ss_handle)
result = qs.rdf_query([((None, "drinks", None),"literal")])
for item in result:
    print "QUERY: Got triple(s): ", item
#    type, triple, ts = item
#    print "Got triple: ", triple, ", stored at", str(ts)

print "Querying: type of x1"
result = qs.wql_nodetypes_query(('x1', False))
for item in result:
    print "QUERY: x1 is of type: ", item

print

print "Querying: is person a subtype of thing"
result = qs.wql_issubtype_query(('person', False), ('thing', False))
print "QUERY: person is a subtype of thing is: ", result

print

print "Querying: x1 and x2 related via 'knows' property"
result = qs.wql_related_query(('x1', False),('x2', False),['seq', 'knows'])
print "QUERY: x1 knows x2 is", result

print

print "Querying: is x1 a person"
result = qs.wql_istype_query(('x1', False), ('person', False))
print "QUERY: 'x1 is a person' is ", result

print

print "Querying: which persons live in Espoo"
result = qs.wql_values_query(('Espoo', True), ['inv', 'lives'])
print "QUERY: persons living in Espoo:", result

node.CloseQueryTransaction(qs)

delete = [(('x2', 'lives', 'Espoo'), 'uri', 'literal')]
ds = node.CreateRemoveTransaction(ss_handle)
ds.remove(delete, confirm = "True")
node.CloseRemoveTransaction(ds)

node.CloseSubscribeTransaction(rs1)
print "Unsubscribing RDF subscription"
node.CloseSubscribeTransaction(rs2)
print "Unsubscribing WQL subscription"
node.leave(ss_handle)
