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
from client_query import *

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

class GameEndedHandler:    

    def __init__(self, player):
        self.player = player
        self.heading = colored("GameEndedHandler> ", "blue", attrs=["bold"])
        self.other_heading = colored("GameEndedHandler> ", "magenta", attrs=["bold"])

    def handle(self, added, removed):
        for t in added:
            message = "Game Ended!"
            color = "green"
            print self.heading + colored(message, color, attrs=["bold"])

            # graphical user interface notification
            if self.player.gtki:
                
                # # label notification
                # self.player.interface.canvas.delete(self.player.interface.balance_editable_label)
                # self.player.interface.balance_editable_label = self.player.interface.canvas.create_text(120, 390, text = message, fill = color, anchor = W)
                        
                # disable every combobox
                self.player.interface.game_sessions_combobox.config(state = DISABLED)
                self.player.interface.actions_combobox.config(state = DISABLED)
                
                # disable buttons
                self.player.interface.choose_game_session_button.config(state = DISABLED)
                self.player.interface.choose_action_button.config(state = DISABLED)

            if self.player.node is not None:            
                self.player.clear_my_sib()

                # closing subs
                self.player.close_subscriptions()
            
                # leaving the sib
                self.player.leave_sib()

        for t in removed:                        
            pass

