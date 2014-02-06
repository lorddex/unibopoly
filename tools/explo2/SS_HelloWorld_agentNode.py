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

#Artificial intelligence to determine does the world exist in the smart space
#Jewish & Christian approach

def DoesWorldExist(WorldCheckList):
    temp = 0
    temp = sum(WorldCheckList.values())
    if temp == 9:
        pro = node.CreateInsertTransaction(ss_handle)

        ConclusionAboutGodsAction = [(("God","hasCreated","World"),
                                      "uri", "literal")]

        # Permant insert without expiring variable
        pro.send(ConclusionAboutGodsAction, confirm = True)
        node.CloseInsertTransaction(pro)

        
# Class structure to be called as subscription fires
class MsgHandler:
    def __init__(self):
        self.results = []
    def handle(self, added, removed):
        print "Newly created:", added
        self.results.extend(added)
        for i in self.results:
           print "State of the space:", str(i)
           # print str(i[0][2])
           # print WorldCheckList 
           if str(i[0][2]) in WorldCheckList:
               WorldCheckList[str(i[0][2])]=1
           else:
               continue
        DoesWorldExist(WorldCheckList)

# Create a reactive-state (reactive) session with the
# smart space

WorldCheckList = {"light":0, "sky":0, "land":0, "sea":0, "sun":0, "moon":0,
                  "stars":0, "animals":0, "man_and_woman":0} 

rs = node.CreateSubscribeTransaction(ss_handle)
result = rs.subscribe_rdf([(('Space', 'has', None ),'literal')], MsgHandler())
if result != []:
    print "State of the space:", result
    for i in result:
        if str(i[0][2]) in WorldCheckList:
            WorldCheckList[str(i[0][2])]=1
        else:
            continue
    DoesWorldExist(WorldCheckList)
   
    
inp = raw_input("Press any key if you are bored to wait\n")
node.CloseSubscribeTransaction(rs)
print "Closing reactive session"
node.leave(ss_handle)
sys.exit()
