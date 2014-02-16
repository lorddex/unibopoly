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
    query = """SELECT ?o
    WHERE { ns:""" + player.nickname + """ ns:cashBalance ?o }"""
    result = player.node.execute_query(query)
    if len(result) == 1:
        balance = int(result[0][0][2])
        return balance
    else: 
        return None

def get_active_player(player):
    query = """SELECT ?o
    WHERE { ns:""" + player.game_session + """ ns:TurnOf ?o}"""
    result = player.node.execute_query(query)
    active_player = str(result[0][0][2].split("#")[1])
    return active_player

# SELF COMMANDS

def get_game_session_status(self, game_session):
    query = """SELECT ?o
    WHERE { ns:""" + game_session + """ ns:HasStatus ?o}"""
    result = self.player.node.execute_query(query)
    game_session_status = str(result[0][0][2].split("#")[1])
    return game_session_status

def get_position_name(self, box_id):
    query = """SELECT ?s
    WHERE { ?s ns:boxID \'""" + str(box_id) + """\'}"""
    result = self.player.node.execute_query(query)
    position_name = str(result[0][0][2].split("#")[1])
    return position_name

def get_box_id(self, position_name):
    query = """SELECT ?o
    WHERE { ns:""" + position_name + """ ns:boxID ?o }"""
    result = self.player.node.execute_query(query)
    box_id = str(result[0][0][2])
    return box_id

def get_box_owner(self, box_name_gs):
    query = """SELECT ?s
    WHERE { ?s ns:HasContract ns:""" + box_name_gs + """}"""
    result = self.player.node.execute_query(query)
    if len(result) > 0:
        box_owner = str(result[0][0][2]).split("#")[1]
    else:
        box_owner = None
    return box_owner

def get_num_of_hotels(self, box_name):
    query = """SELECT ?o
    WHERE { ns:""" + box_name + """ ns:numberOfHotels ?o}"""
    result = self.player.node.execute_query(query) 
    if len(result) == 0:
        return 0
    else:
        num_of_hotels = int(result[0][0][2].split("#")[1])
        return num_of_hotels

def get_possible_commands(self, position_name_gs):
    query = """SELECT ?o
    WHERE { ns:""" + position_name_gs + """ ns:HasPossibleCommand ?o}"""           
    result = self.player.node.execute_query(query)
    return result

def get_position(self):
    query = """SELECT ?o
    WHERE { ns:""" + self.player.nickname + """ ns:IsInBox ?o }"""
    result = self.player.node.execute_query(query)
    if len(result) != 0:
        position = int(result[0][0][2].split("#")[1]) 
    else:
        position = None
    return position

def get_is_in_box(self):
    query = """SELECT ?s ?o
    WHERE { ?s ns:IsInBox ?o }"""
    result = self.player.node.execute_query(query)
    return result
