from smart_m3.m3_kp import *
import uuid
import re
import sys
from termcolor import colored
sys.path.append("../")
from sib import SIBLib
import time
import random 
import Tkinter
from client_query import *

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

class ContractHandler:

    def __init__(self, player):
        self.player = player
        self.heading = colored("ContractHandler> ", "blue", attrs=["bold"])
        self.other_heading = colored("ContractHandler> ", "magenta", attrs=["bold"])
        
    def handle(self, added, removed):
        
        for i in added:
            self.player.lock("contract_handler")

            # retrieving informations
            self.contract_maker =  str(i[0]).split("#")[1]
            self.contract_maker_nickname = self.contract_maker.split("_")[0]
            self.contract_box_name_gs = str(i[2]).split("#")[1]
            self.contract_box_name = self.contract_box_name_gs.split("_")[0] 
            self.contract_gs = self.contract_box_name_gs.split("_")[1] 
            self.contract_box_id = get_box_id(self, self.contract_box_name)
        
            # query = """SELECT ?s
            # WHERE { ?s ns:boxID \'""" + str(self.contract_box) + """\'}"""
            # result = self.player.node.execute_sparql_query(query)
            # self.contract_box_name = str(result[0][0][2]).split("#")[1]

            query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
            WHERE { ns:""" + self.contract_box_name + """ rdf:type ?o }"""

            print "sending contract_handler query" + query
            loop = True
            while loop:
                try:
                    result = self.player.node.execute_sparql_query(query)
                    loop = False
                except SIBError:
                    print "sib error in contract_handler.py"
                                    
            print "QUERY RESULTS (contract_handler): " + str(result)
            self.contract_type = str(result[0][0][2]).split("#")[1]
            
            # printing informations
            if self.contract_gs == self.player.game_session:
                if self.player.nickname == self.contract_maker:
                    print self.heading + "you bought " + colored(self.contract_box_name, "cyan", attrs=["bold"])
                else:
                    print colored("ContractHandler> ", "magenta", attrs=["bold"]) + colored(self.contract_maker_nickname, "cyan", attrs=["bold"]) + " bought " + colored(self.contract_box_name, "cyan", attrs=["bold"])

            # storing informations into the client class
            if self.contract_gs == self.player.game_session:
                self.player.properties[int(self.contract_box_id)]["owner"] = self.contract_maker
                if self.contract_type == "Street":
                    if self.player.properties[int(self.contract_box_id)].has_key("houses"):
                        self.player.properties[int(self.contract_box_id)]["houses"] += 1
                    else:
                        self.player.properties[int(self.contract_box_id)]["houses"] = 1

                # what about graphics?
                if self.player.gtki:
                
                    # determine the color
                    if not(self.player.nickname == self.contract_maker):
                        color = self.player.interface.pieces_colors[self.contract_maker]
                    else:
                        color = "yellow"

                    # determine coordinates for the house
                    top_x = self.player.interface.cell_coords[int(self.contract_box_id)]['x'] - 23
                    top_y = self.player.interface.cell_coords[int(self.contract_box_id)]['y'] - 23
                    bot_x = int(top_x) + 15
                    bot_y = int(top_y) + 15

                    # drawing
                    self.player.interface.houses[str(self.contract_box_id)] = self.player.interface.canvas.create_rectangle(top_x, top_y, bot_x, bot_y, fill=color)
            self.player.unlock("contract_handler")

        for i in removed:
            self.player.lock("contract_handler")


            # retrieving informations
            self.contract_maker =  str(i[0]).split("#")[1]
            self.contract_box_name_gs = str(i[2]).split("#")[1]
            self.contract_box_name = self.contract_box_name_gs.split("_")[0] 
            self.contract_gs = self.contract_box_name_gs.split("_")[1] 
            self.contract_box_id = get_box_id(self, self.contract_box_name)
            
            # debug print
            if self.contract_gs == self.player.game_session:
                if self.contract_maker == self.player.nickname:
                    print self.heading + "you removed the contract for " + colored(str(self.contract_box_name), "cyan", attrs=["bold"])
                else:
                    print self.other_heading + colored(self.contract_maker_nickname, "cyan", attrs=["bold"]) + " removed the contract for " + colored(str(self.contract_box_name), "cyan", attrs=["bold"])

                # storing informations into the client class
                self.player.properties[int(self.contract_box_id)] = {}
        
                # tk user interface
                if self.player.gtki:
                    self.player.interface.canvas.delete(self.player.interface.houses[str(self.contract_box_id)])
                    self.player.interface.houses.pop(str(self.contract_box_id))
                    self.player.properties[int(self.contract_box_id)] = {}

            self.player.unlock("contract_handler")
