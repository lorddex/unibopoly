from smart_m3.m3_kp import *
import uuid
import re
import sys
from termcolor import colored
sys.path.append("../")
from sib import SIBLib
import time
import random
from query import *
import commands 

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

def card_action_pay(self, arg):

    print colored("CommandHandler> ", "blue", attrs=["bold"]) + colored(self.server.current_player, "cyan", attrs=["bold"]) + " pays " + str(arg)

    # get current balance
    current_balance = get_cash_balance(self.server.node, self.server.current_player)
    position = get_position(self.server.node, self.server.current_player)
    new_balance = current_balance - int(arg)
    if int(new_balance) < 0:
        self.server.players.remove(self.server.current_player)
        self.server.number_of_players -= 1
        t_iib = [Triple(URI(ns + self.server.current_player),
                        URI(ns + "IsInBox"),
                        URI(ns + str(position)))]
        self.server.node.remove(t_iib)

    tr = [Triple(URI(ns + self.server.current_player),
                 URI(ns + "cashBalance"),
                 URI(str(current_balance)))]
    ta = [Triple(URI(ns + self.server.current_player),
                 URI(ns + "cashBalance"),
                 URI(str(new_balance)))]
    self.server.node.update(ta, tr)
    commands.switch_turn(self)

def card_action_payall(self, arg):
    print colored("CommandHandler> ", "blue", attrs=["bold"]) + "pay " + str(arg) + " to all the other players"
    current_player = self.server.current_player
    position = get_position(self.server.node, current_player)
    for i in self.server.players:
        if (str(i) != current_player):
            # get balance
            current_balance = get_cash_balance(self.server.node, str(i))
            new_balance = current_balance + int(arg)
            
            tr = [Triple(URI(ns + str(i)),
                         URI(ns + "cashBalance"),
                         URI(str(current_balance)))]
            ta = [Triple(URI(ns + str(i)),
                         URI(ns + "cashBalance"),
                         URI(str(new_balance)))]
            self.server.node.update(ta, tr)
        else:
            num_other_players = self.server.required_players - 1
            # get balance
            current_balance = get_cash_balance(self.server.node, current_player)
            new_balance = current_balance - (int(arg) * num_other_players)
            if int(new_balance) < 0:
                self.server.players.remove(self.server.current_player)
                self.server.number_of_players -= 1
                t_iib = [Triple(URI(ns + self.server.current_player),
                                URI(ns + "IsInBox"),
                                URI(ns + str(position)))]
                self.server.node.remove(t_iib)
            
            tr = [Triple(URI(ns + current_player),
                         URI(ns + "cashBalance"),
                         URI(str(current_balance)))]
            ta = [Triple(URI(ns + current_player),
                         URI(ns + "cashBalance"),
                         URI(str(new_balance)))]
            self.server.node.update(ta, tr)

    commands.switch_turn(self)
    
def card_action_goto(self, arg):
    print colored("CommandHandler> ", "blue", attrs=["bold"]) + colored(self.server.current_player, "cyan", attrs=["bold"]) + " goes to box " + colored(str(arg), "cyan", attrs=["bold"])
    old_position = get_position(self.server.node, self.server.current_player)
    new_position = int(arg)

    #Update Possible commands
    new_box_name = get_box_name(self, new_position)
    commands.update_commands(self, self.server.current_player, new_box_name, new_position)

    tr = [Triple(URI(ns + self.server.current_player),
                 URI(ns + "IsInBox"),
                 URI(ns + str(old_position)))]
    ta = [Triple(URI(ns + self.server.current_player),
                 URI(ns + "IsInBox"),
                 URI(ns + str(new_position)))]
    self.server.node.update(ta, tr)

def card_action_goto_and_earn(self, arg):
    print colored("CommandHandler> ", "blue", attrs=["bold"]) + colored(self.server.current_player.split("_")[0], "cyan", attrs=["bold"]) + " goes to box " + colored(str(arg[0]), "cyan", attrs=["bold"]) + " and earn " + colored(str(arg[1]), "cyan", attrs=["bold"]) + " euro "
    old_position = get_position(self.server.node, self.server.current_player)
    new_position = int(arg[0])

    commands.earn(self, int(arg[1]))

    tr = [Triple(URI(ns + self.server.current_player),
                 URI(ns + "IsInBox"),
                 URI(ns + str(old_position)))]
    ta = [Triple(URI(ns + self.server.current_player),
                 URI(ns + "IsInBox"),
                 URI(ns + str(new_position)))]
    self.server.node.update(ta, tr)
    
  
def card_action_move_forward(self, arg):
    print colored("CommandHandler> ", "blue", attrs=["bold"]) + "move forward " + str(arg)
    old_position = get_position(self.server.node, self.server.current_player)
    new_position = int(old_position) + int(arg)

    #Update Possible commands
    new_box_name = get_box_name(self, new_position)
    commands.update_commands(self, self.server.current_player, new_box_name, new_position)

    tr = [Triple(URI(ns + self.server.current_player),
                 URI(ns + "IsInBox"),
                 URI(ns + str(old_position)))]
    ta = [Triple(URI(ns + self.server.current_player),
                 URI(ns + "IsInBox"),
                 URI(ns + str(new_position)))]
    self.server.node.update(ta, tr)

    
def card_action_move_backward(self, arg):
    print colored("CommandHandler> ", "blue", attrs=["bold"]) + "move backward " + str(arg)
    old_position = get_position(self.server.node, self.server.current_player)
    new_position = int(old_position) - int(arg)

    #Update Possible commands
    new_box_name = get_box_name(self, new_position)
    commands.update_commands(self, self.server.current_player, new_box_name, new_position)

    tr = [Triple(URI(ns + self.server.current_player),
                 URI(ns + "IsInBox"),
                 URI(ns + str(old_position)))]
    ta = [Triple(URI(ns + self.server.current_player),
                 URI(ns + "IsInBox"),
                 URI(ns + str(new_position)))]
    self.server.node.update(ta, tr)
    

def card_action_wait(self, arg):

    print colored("CommandHandler> ", "blue", attrs=["bold"]) + "wait 1 turn"
    self.server.waiting[self.server.current_player] = True
    commands.switch_turn(self)

def card_action_earn(self, arg):
    print colored("CommandHandler> ", "blue", attrs=["bold"]) + "earn " + str(arg)
        
    # get current balance
    current_balance = get_cash_balance(self.server.node, self.server.current_player)
    new_balance = current_balance + int(arg)

    tr = [Triple(URI(ns + self.server.current_player),
                 URI(ns + "cashBalance"),
                 URI(str(current_balance)))]
    ta = [Triple(URI(ns + self.server.current_player),
                 URI(ns + "cashBalance"),
                 URI(str(new_balance)))]
    self.server.node.update(ta, tr)
    commands.switch_turn(self)

def card_action_earnall(self, arg):
    print colored("CommandHandler> ", "blue", attrs=["bold"]) + "earn " + str(arg) + " from each player"
    current_player = self.server.current_player
    position = get_position(self.server.node, current_player)
    for i in self.server.players:
        if (str(i) != current_player):
            # get balance
            current_balance = get_cash_balance(self.server.node, str(i))
            new_balance = current_balance - int(arg)
            if int(new_balance) < 0:
                self.server.players.remove(i)
                self.server.number_of_players -= 1
                t_iib = [Triple(URI(ns + i),
                                URI(ns + "IsInBox"),
                                URI(ns + str(position)))]
                self.server.node.remove(t_iib)
            
            tr = [Triple(URI(ns + str(i)),
                         URI(ns + "cashBalance"),
                         URI(str(current_balance)))]
            ta = [Triple(URI(ns + str(i)),
                         URI(ns + "cashBalance"),
                         URI(str(new_balance)))]
            self.server.node.update(ta, tr)
        else:
            num_other_players = self.server.required_players - 1
            # get balance
            current_balance = get_cash_balance(self.server.node, current_player)
            new_balance = current_balance + (int(arg) * num_other_players)
            
            tr = [Triple(URI(ns + current_player),
                         URI(ns + "cashBalance"),
                         URI(str(current_balance)))]
            ta = [Triple(URI(ns + current_player),
                         URI(ns + "cashBalance"),
                         str(new_balance))]
            self.server.node.update(ta, tr)
            
    commands.switch_turn(self)

    
def card_action_rolldice(self, arg):
    print colored("CommandHandler> ", "blue", attrs=["bold"]) + "roll the dice"
    commands.rolldice(self)


def card_action_jailbreak(self, arg):
    print colored("CommandHandler> ", "blue", attrs=["bold"]) + "prison break!"
    commands.switch_turn(self)
  
