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

class CommandHandler:
    def __init__(self, server):
        self.server = server
        
    def handle(self, added, removed):
        for i in added:

            self.server.lock()
            
            # information retrieval
            command = str(i[0]).split("#")[1]
            issuer = str(i[2]).split("#")[1]
            issuer_game_session = issuer.split("_")[1]

            if issuer_game_session == self.server.game_session_id:
                print colored("CommandHandler> ", "blue", attrs=["bold"]) + colored(issuer.split("_")[0], "cyan", attrs=["bold"]) + " requested " + colored(command, "cyan", attrs=["bold"])

                self.execute_command(command)

            self.server.unlock()

        for i in removed:
            pass


    def execute_command(self, command):
        
        if command == "RollDiceCommand":
            t = [Triple(URI(ns + "RollDiceCommand"),
                        URI(ns + "HasIssuer"),
                        URI(ns + self.server.current_player))]
            self.server.node.remove(t)
            rolldice(self) 
        else:
            if command == "BuildCommand": 
                t = [Triple(URI(ns + "BuildCommand"),
                            URI(ns + "HasIssuer"),
                            URI(ns + self.server.current_player))]
                self.server.node.remove(t)
                print colored("CommandHandler> ", "blue", attrs=["bold"]) + colored("BuildCommand", "cyan", attrs=["bold"]) + " request"
                build(self)
                switch_turn(self)

            elif command == "BuyCommand":
                t = [Triple(URI(ns + "BuyCommand"),
                            URI(ns + "HasIssuer"),
                            URI(ns + self.server.current_player))]
                self.server.node.remove(t)
                print colored("CommandHandler> ", "blue", attrs=["bold"]) + colored("BuyCommand", "cyan", attrs=["bold"]) + " request"
                buy(self)
                switch_turn(self)

            elif command == "TakeHitchCardCommand":
                t = [Triple(URI(ns + "TakeHitchCardCommand"),
                            URI(ns + "HasIssuer"),
                            URI(ns + self.server.current_player))]
                self.server.node.remove(t)
                print colored("CommandHandler> ", "blue", attrs=["bold"]) + colored("TakeHitchCardCommand", "cyan", attrs=["bold"]) + " request"
                takecard(self, "hitch")

            elif command == "TakeProbCardCommand":
                t = [Triple(URI(ns + "TakeProbCardCommand"),
                            URI(ns + "HasIssuer"),
                            URI(ns + self.server.current_player))]
                self.server.node.remove(t)
                print colored("CommandHandler> ", "blue", attrs=["bold"]) + colored("TakeProbCardCommand", "cyan", attrs=["bold"]) + " request"
                takecard(self, "prob")

            elif command == "NothingCommand":
                t = [Triple(URI(ns + "NothingCommand"),
                            URI(ns + "HasIssuer"),
                            URI(ns + self.server.current_player))]
                self.server.node.remove(t)               
                print colored("CommandHandler> ", "blue", attrs=["bold"]) + colored("NothingCommand", "cyan", attrs=["bold"]) + " request"
                switch_turn(self)

            elif command == "PayToOwnerCommand": 
                t = [Triple(URI(ns + "PayToOwnerCommand"),
                            URI(ns + "HasIssuer"),
                            URI(ns + self.server.current_player))]
                self.server.node.remove(t)
                print colored("CommandHandler> ", "blue", attrs=["bold"]) + colored("PayCommand", "cyan", attrs=["bold"]) + " request"
                pay_to_owner(self)
                switch_turn(self)
            
            elif command == "PayCommand": 
                t = [Triple(URI(ns + "PayCommand"),
                            URI(ns + "HasIssuer"),
                            URI(ns + self.server.current_player))]
                self.server.node.remove(t)
                print colored("CommandHandler> ", "blue", attrs=["bold"]) + colored("PayCommand", "cyan", attrs=["bold"]) + " request"
                pay(self)
                switch_turn(self)
