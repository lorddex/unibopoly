import Node
import time

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

class MsgHandler:
    def handle(self, msg):
        for i in msg:
            print "Received:", str(i)

# Create a proactive (sending) session with the
# smart space


# Put information to smart space using the session
# created earlier
# Parameters: string containing the information
#             string containing the information type
# Information and type can be any string, they are
# not restricted by the system

rs = node.CreateSubscribeTransaction(ss_handle)
result = rs.subscribe_rdf([((None, 'lives', None),'literal')], MsgHandler())
print "Subscribe initial result:", result
pro = node.CreateInsertTransaction(ss_handle)
print "--- Connections", node.connections
triples = [(("Ian","lives","Sipoo"),"uri"),(("Jukka","lives","Espoo"),"uri"),
           (("Juergen","lives","Espoo"),"uri"),(("Sipoo","next_to","Helsinki"),"uri"),
           (("Sipoo","next_to","Porvoo"),"uri"), (("Espoo","is_a","city"),"literal"),
           (("Helsinki","is_a","city"),"literal")]
pro.send(triples, confirm = True)
node.CloseInsertTransaction(pro)
print "--- Connections", node.connections

#print "Querying: (*, lives, *)"
#qs = node.CreateQuerySession(ss_handle)
#print "--- Connections", node.connections
#result = qs.query("",(None, "lives", None),"TRIPLE")
#node.CloseQuerySession(qs)
#for item in result:
#    type, triple, ts = item
#    print "Got triple: ", triple, ", stored at", str(ts)
#print "--- Connections", node.connections

print "Querying: (*, next to, *)"
print "--- Connections", node.connections
qs = node.CreateQueryTransaction(ss_handle)
result = qs.rdf_query([((None, "next_to", None),"literal")])
for item in result:
    print "QUERY: Got triple: ", item
#    type, triple, ts = item
#    print "Got triple: ", triple, ", stored at", str(ts)

print "Querying: (*, next to, Porvoo)"
result = qs.rdf_query([((None, "next_to", "Porvoo"),"uri")])
for item in result:
    print "QUERY: Got triple: ", item

print "Querying: (Sipoo, next to, *)"
result = qs.rdf_query([(("Sipoo", "next_to", None),"uri")])
for item in result:
    print "QUERY: Got triple: ", item

print "Querying: (*, is_a, city)"
result = qs.rdf_query([((None, "is_a", "city"),'literal')])
for item in result:
    print "QUERY: Got triple: ", item




node.CloseQueryTransaction(qs)

print "--- Connections", node.connections
node.CloseSubscribeTransaction(rs)
print "Closing reactive session"
node.leave(ss_handle)
