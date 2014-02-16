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
from query import *

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

class CommandHandler:
    def __init__(self, server):
        self.server = server
        self.heading = colored("CommandHandler> ", "blue", attrs=["bold"])
        
    def handle(self, added, removed):
        for i in added:

            self.server.lock()
                        
            # information retrieval
            command = str(i[0]).split("#")[1]
            command_type = command.split("_")[0]
            issuer = str(i[2]).split("#")[1]
            issuer_game_session = issuer.split("_")[1]

            issuer_position = get_position(self.server.node, issuer)
            box_name = get_box_name(self, issuer_position)
            cmds = get_commands(self.server.node, box_name+"_"+issuer_game_session)
            box_type = get_box_type(self, box_name)
 
            if command_type != "RollDiceCommand" and command_type != "TakeHitchCardCommand" and command_type != "TakeProbCardCommand" and box_type != "Special" and command_type not in cmds:
                print self.heading + "COMMAND " + command + " IS NOT A POSSIBLE COMMAND FOR THIS BOX!! CHEAT ATTEMPT, QUITTING."
                self.server.unlock()
                self.server.close_subscriptions()
                self.server.leave_sib()
                sys.exit(0)                

            if issuer_game_session == self.server.game_session_id:
                print self.heading + colored(issuer.split("_")[0], "cyan", attrs=["bold"]) + " requested " + colored(command, "cyan", attrs=["bold"])          
                self.execute_command(command, command_type)

            self.server.unlock()

        for i in removed:
            pass


    def execute_command(self, command, command_type):

        # removing triples
        self.remove_command(command, command_type)
        
        # executing commands
        if command_type == "RollDiceCommand":
            rolldice(self) 
        else:
            if command_type == "BuildCommand": 
                print self.heading + colored("BuildCommand", "cyan", attrs=["bold"]) + " request"
                build(self)
                switch_turn(self)

            elif command_type == "BuyCommand":
                print self.heading + colored("BuyCommand", "cyan", attrs=["bold"]) + " request"
                buy(self)
                switch_turn(self)

            elif command_type == "TakeHitchCardCommand":
                print self.heading + colored("TakeHitchCardCommand", "cyan", attrs=["bold"]) + " request"
                takecard(self, "hitch")

            elif command_type == "TakeProbCardCommand":
                print self.heading + colored("TakeProbCardCommand", "cyan", attrs=["bold"]) + " request"
                takecard(self, "prob")

            elif command_type == "NothingCommand":
                print self.heading + colored("NothingCommand", "cyan", attrs=["bold"]) + " request"
                switch_turn(self)

            elif command_type == "PayToOwnerCommand":
                print self.heading + colored("PayCommand", "cyan", attrs=["bold"]) + " request"
                pay_to_owner(self)
                switch_turn(self)
            
            elif command_type == "PayCommand": 
                print self.heading + colored("PayCommand", "cyan", attrs=["bold"]) + " request"
                pay(self)
                switch_turn(self)

    # the following function is used to easily delete the command-related triples
    # before executing a command

    def remove_command(self, command, command_type):

        # finding triples to remove
        t = []        
        t.append(Triple(URI(ns + command),
                        URI(ns + "HasIssuer"),
                        URI(ns + self.server.current_player)))
        t.append(Triple(URI(ns + command),
                        URI(rdf + "type"),
                        URI(ns + "Command")))
        t.append(Triple(URI(ns + command),
                        URI(ns + "HasCommandType"),
                        URI(ns + command_type)))
        
        # removing triples
        self.server.node.remove(t)
