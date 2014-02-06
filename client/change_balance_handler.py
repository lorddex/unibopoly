from smart_m3.m3_kp import *
import uuid
import re
import sys
from termcolor import colored
sys.path.append("../")
from sib import SIBLib
import time
from Tkinter import *
from PIL import ImageTk, Image
import tkFont
from tkMessageBox import showinfo


rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

class ChangeBalanceHandler:

    def __init__(self, player):
        self.player = player
        self.current_player = None
        self.current_player_nickname = None
        self.updated_balance = None
        self.heading = colored("ChangeBalanceHandler> ", "blue", attrs=["bold"])
        self.other_heading = colored("ChangeBalanceHandler> ", "magenta", attrs=["bold"])
        
    def handle(self, added, removed):
        for t in added:
            self.player.lock("change balance")

            # retrieving informations
            self.updated_balance = str(t[2]).split("#")[1]
            self.current_player = str(t[0]).split("#")[1]            
            self.current_player_nickname = self.current_player.split("_")[0]
            self.player.balance = self.updated_balance
            
            # check if the player lost the game
            if int(self.updated_balance) < 0:

                # check who lost the game
                if self.player.nickname == self.current_player:
                    print self.heading + colored("you lost the game!", "red", attrs=["bold"])
                else:
                    print self.other_heading + colored(self.current_player_nickname + " lost the game!", "red", attrs=["bold"])

                # check how many players remain
                
                # graphical user interface notifications
                if self.player.gtki:

                    if self.player.nickname == self.current_player:
                        # Action Label
                        self.player.interface.canvas.delete(self.player.interface.balance_editable_label)
                        self.player.interface.balance_editable_label = self.player.interface.canvas.create_text(120, 390, text = "You lost the game!", anchor = W)
                    
                        # disable every combobox
                        self.player.interface.game_sessions_combobox.config(state = DISABLED)
                        self.player.interface.actions_combobox.config(state = DISABLED)
                    
                        # disable buttons
                        self.player.interface.choose_game_session_button.config(state = DISABLED)
                        self.player.interface.choose_action_button.config(state = DISABLED)
                    
                    # delete the piece
                    if self.player.nickname == self.current_player:
                            self.player.interface.canvas.delete(self.player.interface.piece)
                    else:
                        self.player.interface.canvas.delete(self.player.interface.pieces[self.current_player])

                if self.player.nickname == self.current_player:

                    self.player.clear_my_sib()
                    self.player.begin_observer()

            else:

                # simply notify the updated balance                
                if self.player.nickname == self.current_player:
                    print self.heading + "you have now " + str(self.updated_balance) + " euros"


                    # always update the label in the gui
                    if self.player.gtki:
                        self.player.interface.canvas.delete(self.player.interface.balance_editable_label)
                        self.player.interface.balance_editable_label = self.player.interface.canvas.create_text(120, 390, text = str(self.player.balance), anchor = W)

            self.player.unlock("change_balance")

        # removed triples
        for t in removed:
            pass
