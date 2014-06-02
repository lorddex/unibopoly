from smart_m3.m3_kp import *
import uuid
import re
import sys
from termcolor import colored
sys.path.append("../")
from sib import SIBLib
import time

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

class ActivateGameSessionHandler:
    def __init__(self, server):
        self.server = server
        self.heading = colored("ActivateGameSessionHandler> ", 'red', attrs=['bold'])

    def handle(self, added, removed):
        for i in added:
            self.server.lock()
            
            # filling the players array
            query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o 
            WHERE { ns:""" + self.server.game_session_id + """
                ns:HasPlayer
                ?o
            }"""     
            result = self.server.node.execute_sparql_query(query)

            for player in result:
                for el in player:
                    self.server.players.append(el[2].split('#')[1])        
                    print self.heading + "added " + colored(el[2].split('#')[1].split("_")[0], "cyan", attrs=["bold"]) + " to " + colored(self.server.game_session_id, "cyan", attrs=["bold"])
                    self.server.number_of_players += 1
                

            # setting the turn 
            triple = [Triple(URI(ns + self.server.game_session_id),
                             URI(ns + "TurnOf"),
                             URI(ns + self.server.players[0]))]
            self.server.node.insert(triple)

            # setting game session status
            ta = [Triple(URI(ns + self.server.game_session_id),
                                 URI(ns + "HasStatus"),
                                 URI(ns + "Active"))]
            tr = [Triple(URI(ns + self.server.game_session_id),
                                 URI(ns + "HasStatus"),
                                 URI(ns + "Waiting"))]
            self.server.node.update(ta, tr)        
            
            print self.heading + "setting turn to " + colored(self.server.players[0].split("_")[0], "cyan", attrs=["bold"])
            print self.heading + "changing game session status to " + colored("Active", "cyan", attrs=["bold"])
            self.server.current_player = self.server.players[0]
            self.server.current_player_id = 0

            self.server.unlock()

        for i in removed:
            pass
        
