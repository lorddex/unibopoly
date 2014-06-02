from smart_m3.m3_kp import *
import uuid
import re
import sys
from termcolor import colored
sys.path.append("../")
from sib import SIBLib
import time
import random

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

# GENERAL
def get_balance(player):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + player.nickname + """ ns:cashBalance ?o }"""
    result = player.node.execute_sparql_query(query)
    if len(result) == 1:
        balance = int(result[0][0][2])
        return balance
    else: 
        return None

def get_active_player(player):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + player.game_session + """ ns:TurnOf ?o}"""
    result = player.node.execute_sparql_query(query)
    active_player = str(result[0][0][2].split("#")[1])
    return active_player

# SELF COMMANDS

def get_purchase_cost(self, box_name):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + box_name + """ ns:purchaseCost ?o}"""
    result = self.player.node.execute_sparql_query(query)
    if len(result) > 0:
        purchaseCost = int(result[0][0][2])
    else:
        purchaseCost = None
    return purchaseCost

def get_game_session_status(self, game_session):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + game_session + """ ns:HasStatus ?o}"""
    result = self.player.node.execute_sparql_query(query)
    game_session_status = str(result[0][0][2].split("#")[1])
    return game_session_status

def get_position_name(self, box_id):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?s
    WHERE { ?s ns:boxID \'""" + str(box_id) + """\'}"""
    print query
    result = self.player.node.execute_sparql_query(query)
    position_name = str(result[0][0][2].split("#")[1])
    return position_name

def get_box_id(self, position_name):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + position_name + """ ns:boxID ?o }"""
    result = self.player.node.execute_sparql_query(query)
    box_id = str(result[0][0][2])
    return box_id

def get_box_owner(self, box_name_gs):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?s
    WHERE { ?s ns:HasContract ns:""" + box_name_gs + """}"""
    print query
    result = self.player.node.execute_sparql_query(query)
    if len(result) > 0:
        box_owner = str(result[0][0][2]).split("#")[1]
    else:
        box_owner = None
    return box_owner

def get_num_of_hotels(self, box_name):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + box_name + """ ns:numberOfHotels ?o}"""
    result = self.player.node.execute_sparql_query(query) 
    if len(result) == 0:
        return 0
    else:
        num_of_hotels = int(result[0][0][2].split("#")[1])
        return num_of_hotels

def get_possible_commands(self, position_name_gs):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + position_name_gs + """ ns:HasPossibleCommand ?o}"""           
    result = self.player.node.execute_sparql_query(query)
    return result

def get_position(self):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + self.player.nickname + """ ns:IsInBox ?o }"""
    result = self.player.node.execute_sparql_query(query)
    if len(result) != 0:
        position = int(result[0][0][2].split("#")[1]) 
    else:
        position = None
    return position

def get_is_in_box(self):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?s ?o
    WHERE { ?s ns:IsInBox ?o }"""
    result = self.player.node.execute_sparql_query(query)
    return result

def get_is_in_box_gs(self, gs):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?s ?o
    WHERE { ?s ns:IsInBox ?o }"""
    result = self.player.node.execute_sparql_query(query)
    num = 0
    if result != None:
        for i in result:
            if i[0][2].split('_')[1] == gs:
                num = num + 1
    return num
