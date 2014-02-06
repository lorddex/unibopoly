from client import MM3Client
from smart_m3.m3_kp import *
import uuid
import re
import sys
from termcolor import colored
sys.path.append("../")
from sib import SIBLib
import time
import re

if len(sys.argv) < 4: 
    print "Wrong number of arguments! You should use:"
    print "$ python client.py server_ip server_port role"
    sys.exit(0)

# client connection
c = MM3Client.MM3Client(sys.argv[1], int(sys.argv[2]), True, False, None)

# nickname request
reg = re.compile(r"[a-zA-Z0-9_]*$")
nickname = raw_input("Insert a nickname > ")

while not(reg.match(nickname)) or nickname == "":
    print "Nickname not valid!"
    nickname = raw_input("Insert another nickname > ")
        
# game session selection
game_session_list = c.get_game_session_list()
if len(game_session_list)>0:          
    print  colored("Client> ", "yellow", attrs=["bold"]) + "select the desired game session: "
    index = 1
    gs_id = []
    for i in game_session_list:
        query2 = """
        SELECT ?p
        WHERE {ns:""" + i + """ ns:numberOfPlayers ?p}
        """
        res = c.node.execute_query(query2)
        print colored("Client> ", "yellow", attrs=["bold"]) + "write " + str(index) + " for the game session " + colored(i, "cyan", attrs=["bold"]) + " (users: " + str(res[0][0][2].split('#')[1]) + ")" 
        gs_id.append(str(index))
        index += 1

    gs = None
    while not(str(gs) in gs_id):
        try:
            gs = input(colored("Client> ", "yellow", attrs=["bold"]))
        except Exception:
            print  colored("Client> ", "yellow", attrs=["bold"]) + "game session inesistente! Inserire nuovamente:" 
    
    gamesession = game_session_list[gs-1]

# game session connection
c.join_game_session(gamesession, sys.argv[3], nickname)

# subscriptions
c.launch_subscriptions()
