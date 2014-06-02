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

#    # print 'sending get_balance query: ' + query

    loop = True
    while loop:
        try:
            result = player.node.execute_sparql_query(query)
            loop = False
        except SIBError:
            print "sib error on get_balance"

#    # print "QUERY RESULTS (get_balance): " + str(result)

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
    # print 'sending get_active_player query' + query

    loop = True
    while loop:
        try:
            result = player.node.execute_sparql_query(query)
            loop = False
        except SIBError:
            print "sib error on get_active_player"

    # print "QUERY RESULTS (get_active_player): " + str(result)
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
    # print 'sending get_purchase_cost query' + query

    loop = True
    while loop:
        try:
            result = self.player.node.execute_sparql_query(query)
            loop = False
        except SIBError:
            print "sib error on get_purchase_cost"

    # print "QUERY RESULTS (get_purchase_cost): " + str(result)
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
    # print 'sending get_game_session_status query' + query

    loop = True
    while loop:
        try:
            result = self.player.node.execute_sparql_query(query)
            loop = False
        except SIBError:
            print "sib error on get_game_session_status"

    # print "QUERY RESULTS (get_game_session_status): " + str(result)
    game_session_status = str(result[0][0][2].split("#")[1])
    return game_session_status

def get_position_name(self, box_id):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?s WHERE { ?s ns:boxID '""" + str(box_id) + """'}"""
    # print 'sending get_position_name query' + query

    loop = True
    while loop:
        try:
            result = self.player.node.execute_sparql_query(query)
            loop = False
        except SIBError:
            print "sib error on get_position_name"

    # print "QUERY RESULTS (get_position_name): " + str(result)
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
    # print 'sending get_box_id query' + query

    loop = True
    while loop:
        try:
            result = self.player.node.execute_sparql_query(query)
            loop = False
        except SIBError:
            print 'sib error on get_box_id'

    # print "QUERY RESULTS (get_box_id): " + str(result)
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
    # print 'sending get_box_owner query' + query

    loop = True
    while loop:
        try:
            result = self.player.node.execute_sparql_query(query)
            loop = False
        except SIBError:
            print 'sib error on get_box_owner'

    # print "QUERY RESULTS (get_box_owner): " + str(result)
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
    # print 'sending get_num_of_hotels query' + query

    loop = True
    while loop:
        try:
            result = self.player.node.execute_sparql_query(query) 
            loop = False
        except SIBError:
            print 'sib error on get_num_of_hotels'

    # print "QUERY RESULTS (get_num_of_hotels): " + str(result)
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
    # print 'sending get_possible_commands query' + query

    loop = True
    while loop:
        try:
            result = self.player.node.execute_sparql_query(query)
            loop = False
        except SIBError:
            print 'sib error on get_possible_commands'

    # print "QUERY RESULTS (get_possible_commands): " + str(result)
    return result

def get_position(self):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?o
    WHERE { ns:""" + self.player.nickname + """ ns:IsInBox ?o }"""
    # print 'sending get_position query' + query

    loop = True
    while loop:
        try:
            result = self.player.node.execute_sparql_query(query)
            loop = False
        except SIBError:
            print "sib error on get_position"

    # print "QUERY RESULTS (get_position): " + str(result)
    if len(result) != 0:
        try:
            position = int(result[0][0][2]) 
        except ValueError:
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
    # print 'sending get_is_in_box query' + query

    loop = True
    while loop:
        try:
            result = self.player.node.execute_sparql_query(query)
            loop = False
        except SIBError:
            print 'sib error on get_is_in_box'

    # print "QUERY RESULTS (get_is_in_box): " + str(result)
    return result

def get_is_in_box_gs(self, gs):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?s ?o
    WHERE { ?s ns:IsInBox ?o }"""
    # print 'sending get_is_in_box_gs query' + query

    loop = True
    while loop:
        try:
            result = self.player.node.execute_sparql_query(query)
            loop = False
        except SIBError:
            print 'sib error on get_is_in_box_gs'

    # print "QUERY RESULTS (get_is_in_box_gs): " + str(result)
    num = 0
    if result != None:
        for i in result:
            if i[0][2].split('_')[1] == gs:
                num = num + 1
    return num
