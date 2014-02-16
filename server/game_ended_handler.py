from smart_m3.m3_kp import *
import uuid
import re
import sys
from termcolor import colored
sys.path.append("../")
from sib import SIBLib
import time
import random
from commands import *

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

# This handler starts when a player is removed

class GameEndedHandler:
    def __init__(self, server):
        self.server = server
        self.heading = colored("GameEndedHandler> ", "blue", attrs=["bold"])
        
    def handle(self, added, removed):

        for i in added:
            pass

        for i in removed:
            
            # lock
            self.server.lock()
            
            for j in self.server.players:
                if j == str(removed[0][2]).split('#')[1]:
                    self.server.players.remove(j)

            # check how many players remains. If it's only one player, then the game is ended
            if len(self.server.players) == 1:
                
                # and the winner is...
                print self.heading + colored(self.server.players[0], "cyan", attrs=["bold"]) + " won the game!"

                # updating the triple into the sib
                tr = [Triple(URI(ns + self.server.game_session_id),
                             URI(ns + "HasStatus"),
                             URI(ns + "Active"))]
                ta = [Triple(URI(ns + self.server.game_session_id),
                             URI(ns + "HasStatus"),
                             URI(ns + "Ended"))]
                self.server.node.update(ta, tr)

                # closing subs
                self.server.close_subscriptions()

                # leaving the sib
                self.server.leave_sib()
            # else:
            #     print "RICHIAMO LA SWITCH TURN DA GAME ENDED HANDLER"
            #     switch_turn(self)
                

            # unlock
            self.server.unlock()
