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

# GENERAL QUERIES
def get_players(node, session):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + session + """ ns:HasPlayer ?o }"""
    result = node.execute_sparql_query(query)
    res = []
    if len(result)>0:
        for i in result:
            res.append(str(i[0][2]).split("#")[1])
    return res

def get_commands(node, box_name):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
        WHERE {ns:""" + box_name + """ ns:HasPossibleCommand ?o }"""
    result = node.execute_sparql_query(query) 
    cmds = []
    for i in result:
       cmds.append(str(i[0][2]).split("#")[1])

    return cmds

def get_cash_balance(node, player):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + player + """ ns:cashBalance ?o}"""
    result = node.execute_sparql_query(query)
    cash_balance = int(result[0][0][2])
    return cash_balance

def get_position(node, player):
    # Get old position
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + player + """ ns:IsInBox ?o}"""
    result = node.execute_sparql_query(query)
    position = result[0][0][2].split("#")[1]
    return position

# COMMANDS QUERIES
def get_current_gs(self, player):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?s 
    WHERE { ?s ns:HasPlayer ns:""" + player + """ }"""
    result = self.server.node.execute_sparql_query(query)
    gs = result[0][0][2].split("#")[1]
    return str(gs)

def get_box_name(self, position):
    # Get position name
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?s
    WHERE { ?s  ns:boxID \'""" + str(position) + """\'}"""
    result = self.server.node.execute_sparql_query(query)
    box_name = str(result[0][0][2].split("#")[1])
    return box_name

def get_box_color(self, position_name):
    # Get position color
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + position_name + """ ns:boxColor ?o }"""
    print query
    result = self.server.node.execute_sparql_query(query)
    box_color = str(result[0][0][2])
    return box_color

def get_boxes_with_color_same_as(self, position_name):
    # Get boxes with color same as the given box
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?s
    WHERE { ns:""" + position_name + """ ns:boxColor ?c .
    ?s ns:boxColor ?c }"""
    result = self.server.node.execute_sparql_query(query)
    boxes = []
    for r in result:
        boxes.append(str(r[0][2]).split("#")[1])
    return boxes

def get_box_owner(self, box_name_gs):
    # query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    # WHERE { ?s ns:HasContract ns:""" + str(position) + """}"""
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?s
    WHERE { ?s ns:HasContract ns:""" + box_name_gs + """}"""
                        
    result = self.server.node.execute_sparql_query(query)
    if len(result)>0:                
        owner = str(result[0][0][2].split('#')[1])
        return owner
    else:
        return None
    
#def get_cash_balance(self, player):
#    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#    WHERE { ns:""" + player + """ ns:cashBalance ?o}"""
#    result = self.server.node.execute_sparql_query(query)
#    cash_balance = int(result[0][0][2].split("#")[1])
#    return cash_balance

def get_purchase_cost(self, box_name):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + box_name + """ ns:purchaseCost ?o}"""
    result = self.server.node.execute_sparql_query(query)
    purchaseCost = int(result[0][0][2])
    return purchaseCost

def get_toll_cost(self, box_name):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + box_name + """ ns:tollCost ?o}"""
    result = self.server.node.execute_sparql_query(query)
    tollCost = int(result[0][0][2])
    return tollCost

def get_num_of_houses(self, box_name):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + box_name + """ ns:numberOfHouses ?o}"""
    result = self.server.node.execute_sparql_query(query) 
    if len(result) == 0:
        return 0
    else:
        num_of_houses = int(result[0][0][2])
        return num_of_houses

def get_num_of_hotels(self, box_name):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + box_name + """ ns:numberOfHotels ?o}"""
    result = self.server.node.execute_sparql_query(query) 
    if len(result) == 0:
        return 0
    else:
        num_of_hotels = int(result[0][0][2])
        return num_of_hotels

def get_box_type(self, box_name):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE {ns:""" + box_name + """ rdf:type ?o}"""
    result = self.server.node.execute_sparql_query(query)
    box_type = str(result[0][0][2].split('#')[1]) 
    return box_type



