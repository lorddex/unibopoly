import Node
import time
import sys

# Create a node instance
# Programmer can give any name 
# The infrastucture will assign unigue names ???
node = Node.ParticipantNode("SS_HelloWorld_ProactiveNode")

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

# end connecting 

# Create Insert transaction with the
# smart space

pro = node.CreateInsertTransaction(ss_handle)
print "Starting insert"
#pro = node.CreateProactiveSession(ss_handle)

InformationAboutGodsAction = [(("Space","has","light"),"uri", "literal"),
                              (("Space","has","land"),"uri", "literal"),
                              (("Space","has","animals"),"uri", "literal"),
                              (("Space","has","stars"),"uri", "literal"),
                              (("Space","has","man_and_woman"),"uri", "literal"),
                              (("Space","has","sky"),"uri", "literal"),
                              (("Space","has","moon"),"uri", "literal"),
                              (("Space","has","sea"),"uri", "literal"),
                              (("Space","has","sun"),"uri", "literal")]

# Insert
pro.send(InformationAboutGodsAction, confirm = True)
node.CloseInsertTransaction(pro)
print "Insert done"

# Disconnect from the smart space
# The information stays
node.leave(ss_handle)
sys.exit()
