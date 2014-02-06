import Node
import time
import sys

# Create a node instance
# Programmer can give any name 
# The infrastucture will assign unigue names ???
node = Node.ParticipantNode("HelloWorld reactive")




# Discover Smart Spaces around you
# Use the technologies used at the "vertical business domain"
# E.g. mDNS, UPnP, UDDI, Bluetooth SDP


# Connect to the selected smart space
# In this simple example we use localhost
#ss_handle = ("X", (Node.TCPConnector, ("127.0.0.1", 10011)))

ss_handle = node.discover()

print ss_handle

if not node.join(ss_handle):
    sys.exit('Could not join to Smart Space')

print "--- Member of SS:", node.member_of
# end connenct

# Class structure to be called as subscription fires
class MsgHandler:
    def __init__(self):
        self.results = []
    def handle(self, added, removed):
        print "Newly created:", added
        self.results.extend(added)
        for i in self.results:
            print "State of the space:", str(i)
            print str(i[0][2])
        print "HelloWorld"
        node.CloseSubscribeTransaction(rs)
        print "Closing reactive session"
        node.leave(ss_handle)
        sys.exit()

# Create a reactive-state (reactive) session with the
# smart space


rs = node.CreateSubscribeTransaction(ss_handle)
result = rs.subscribe_rdf([(('God', 'hasCreated', 'World'),'literal')], MsgHandler())


if result != []:
    print "It seem The God has already done his job thus..."
    print "HelloWorld"
    node.CloseSubscribeTransaction(rs)
    print "Unsubscribed"
    node.leave(ss_handle)
    
inp = raw_input("Press any key if you are bored to wait\n")
node.CloseSubscribeTransaction(rs)
print "Unsubscribed"
node.leave(ss_handle)
sys.exit()
