from smart_m3.m3_kp import *
import uuid
import re
import sys
from termcolor import colored
sys.path.append("../")
from sib import SIBLib
import time
import Tkinter
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

class TurnHandler:
    def __init__(self, player):
        self.player = player
        self.current_player = None
        self.current_player_nickname = None
        self.heading = colored("TurnHandler> ", "blue", attrs=["bold"])
        self.other_heading = colored("TurnHandler> ", "magenta", attrs=["bold"])
        
    def handle(self, added, removed):

        for i in added:

            # retrieving informations
            self.current_player = str(i[2]).split("#")[1]
            self.current_player_nickname = self.current_player.split("_")[0]

            if self.current_player == self.player.nickname:

                self.player.lock("turn_handler")

                # retrieving position
                self.player.current_position = get_position(self)

                # retrieving balance 
                balance = get_balance(self.player)

                if int(balance) >= 0:

                    self.player.balance = balance
                    if self.player.waiting == False:
                        print self.heading + "it's your turn! --- you are in box " + str(self.player.current_position) + " and you have " + str(self.player.balance) + " euros"

                    # check if we won the game!                
                    np_result = get_is_in_box(self)
                    
                    if len(np_result) == 1:
                
                        print self.heading + colored("you won the game! CONGRATULATIONS!", "green", attrs=["bold"])

                        # graphical user interface notification
                        if self.player.gtki:
                            self.player.interface.canvas.delete(self.player.interface.balance_editable_label)
                            self.player.interface.balance_editable_label = self.player.interface.canvas.create_text(120, 390, text = "You won the game!", fill = "green", anchor = W)
                            
                            # disable every combobox
                            self.player.interface.game_sessions_combobox.config(state = DISABLED)
                            self.player.interface.actions_combobox.config(state = DISABLED)
                    
                            # disable buttons
                            self.player.interface.choose_game_session_button.config(state = DISABLED)
                            self.player.interface.choose_action_button.config(state = DISABLED)
                
                    else:

                        # Increment the turn number
                        self.player.turn_number += 1

                        if self.player.gtki:

                            self.player.interface.actions_combobox_var.set('')
                            m = self.player.interface.actions_combobox['menu']
                            m.delete(0, 'end')

                            if self.player.waiting == False:
                                m.add_command(label = "RollDiceCommand", command=Tkinter._setit(self.player.interface.actions_combobox_var, "RollDiceCommand"))
                            else:
                                m.add_command(label = "NothingCommand", command=Tkinter._setit(self.player.interface.actions_combobox_var, "NothingCommand"))
                                self.player.waiting = False
                        
                            m = self.player.interface.actions_combobox.pack() 
                            self.player.interface.actions_combobox.config(state = NORMAL)
                            self.player.interface.choose_action_button.config(state = NORMAL)

                            # updating informations in the labels
                            self.player.interface.canvas.delete(self.player.interface.balance_editable_label)
                            self.player.interface.balance_editable_label = self.player.interface.canvas.create_text(120, 390, text = str(self.player.balance), anchor = W)
                            self.player.interface.turn_editable_label.config(text = "YOU!")
 
                        else: # command line interface

                            # Roll the dices request
                            if self.player.waiting == False:
                                print self.heading + "available actions:"
                                print self.heading + "[0] " + colored("RollDiceCommand", "cyan", attrs=["bold"])
     
                                action = None            
                                while (action != 0):
                                    try:
                                        print self.heading + "Action? "
                                        while self.player.command_available is False and self.player.quit is False:
                                            time.sleep(0.1)
                                        if self.player.quit is True:
                                            return
                                        action = int(self.player.extract_command())
                                    except EOFError:
                                        print "Goodbye!"    
                                        self.player.force_quit()
                                        sys.exit(0)
                
                                    print self.heading + " user chose command " + colored("RollDiceCommand", "cyan", attrs=["bold"])
                                    
                                t = []
                                t.append(Triple(URI(ns + "RollDiceCommand_" + str(self.player.turn_number)),
                                            URI(ns + "HasIssuer"),
                                            URI(ns + self.player.nickname)))
                                t.append(Triple(URI(ns + "RollDiceCommand_" + str(self.player.turn_number)),
                                            URI(rdf + "type"),
                                            URI(ns + "Command")))
                                t.append(Triple(URI(ns + "RollDiceCommand_" + str(self.player.turn_number)),
                                            URI(ns + "HasCommandType"),
                                            URI(ns + "RolldiceCommand")))

                                self.player.node.insert(t)
                                print self.heading + " adding a " + colored("RollDice", "cyan", attrs=["bold"]) + " request"
                            else:

                                # if the player is blocked in secretary he can only wait!
                                t = []
                                t.append(Triple(URI(ns + "NothingCommand_" + str(self.player.turn_number)),
                                                URI(ns + "HasIssuer"),
                                                URI(ns + self.player.nickname)))
                                t.append(Triple(URI(ns + "NothingCommand_" + str(self.player.turn_number)),
                                            URI(rdf + "type"),
                                            URI(ns + "Command")))
                                t.append(Triple(URI(ns + "NothingCommand_" + str(self.player.turn_number)),
                                            URI(ns + "HasCommandType"),
                                            URI(ns + "NothingCommand")))                                
                                self.player.node.insert(t)

                                # reset the waiting status
                                self.player.waiting = False
                                
                self.player.unlock("turn_handler")

            else: # it isn't my turn
                print self.other_heading + "it's " + colored(str(self.current_player_nickname), "cyan", attrs=["bold"]) + "'s turn"
                if self.player.gtki:
                    self.player.interface.turn_editable_label.config(text = str(self.current_player.split("_")[0]), anchor = W)
                    self.player.interface.actions_combobox.config(state = DISABLED)
                    self.player.interface.choose_action_button.config(state = DISABLED)


        for i in removed:
            pass
