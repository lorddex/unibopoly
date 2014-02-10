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

class NumberOfHousesHandler:

    def __init__(self, player):
        self.player = player
        self.number = None
        self.box_id = None
        self.box_name = None
        self.owner = None
        self.headings = colored("NumberOfHousesHandler> ", "blue", attrs=["bold"])
        self.other_headings = colored("NumberOfHousesHandler> ", "magenta", attrs=["bold"])
        
    def handle(self, added, removed):
        for i in added:
            self.player.lock("number_of_houses")
            
            # information retrieval
            self.number = str(i[2]).split("#")[1]
            self.box_name_gs = str(i[0]).split("#")[1]
            self.box_name = self.box_name_gs.split("_")[0]
            self.box_id = get_box_id(self, self.box_name)
            self.gs = self.box_name_gs.split("_")[1]
            self.owner = get_box_owner(self, self.box_name_gs)

            # storing informations
            if self.gs == self.player.game_session:
                if int(self.number) > 1: # the first time this info is updated by the contract_handler
                    self.player.properties[int(self.box_id)]["houses"] += 1

                # debug print
                if self.owner == self.player.nickname:
                    print self.headings + "you built the house n." + str(self.number)
                else:
                    print self.other_headings + colored(self.owner.split("_")[0], "cyan", attrs=["bold"]) + " built the house n." + str(self.number)

                # tk user interface
                if self.player.gtki:             
                    if int(self.number) > 1: # we need to enlarge the house!

                        # determine the color
                        if not(self.player.nickname == self.owner):
                            color = self.player.interface.pieces_colors[self.owner]
                        else:
                            color = "yellow"

                        # determine coordinates for the house
                        top_x = self.player.interface.cell_coords[int(self.box_id)]['x'] - 23
                        top_y = self.player.interface.cell_coords[int(self.box_id)]['y'] - 23
                        bot_x = int(top_x) + 15 * int(self.number)
                        bot_y = int(top_y) + 15

                        # delete the old house
                        self.player.interface.canvas.delete(self.player.interface.houses[str(self.box_id)])

                        # build the new house
                        self.player.interface.houses[str(self.box_id)] = self.player.interface.canvas.create_rectangle(top_x, top_y, bot_x, bot_y, fill=color)
            self.player.unlock("number_of_houses")

        # houses removal

        for t in removed:

            self.player.lock("number_of_houses")

            # we need to check if the houses became hotels

            # information retrieval

            self.box_name_gs = str(t[0]).split("#")[1]
            self.box_name = self.box_name_gs.split("_")[0]
            self.box_id = get_box_id(self, self.box_name)
            self.gs = self.box_name_gs.split("_")[1]
            self.owner = get_box_owner(self, self.box_name_gs)
            self.hotels = get_num_of_hotels(self, self.box_name_gs)

            if int(self.hotels) == 1:
                
                # tk user interface
                if self.player.gtki:             
                    
                    # determine the color
                    if not(self.player.nickname == self.owner):
                        color = self.player.interface.pieces_colors[self.owner]
                    else:
                        color = "yellow"
                        
                    # determine coordinates for the house
                    top_x = self.player.interface.cell_coords[int(self.box_id)]['x'] - 23
                    top_y = self.player.interface.cell_coords[int(self.box_id)]['y'] - 23
                    bot_x = int(top_x) + 15 * 4
                    bot_y = int(top_y) + 15
    
                    # delete the old house
                    self.player.interface.canvas.delete(self.player.interface.houses[str(self.box_id)])
    
                    # build the new house
                    self.player.interface.houses[str(self.box_id)] = self.player.interface.canvas.create_rectangle(top_x, top_y, bot_x, bot_y, fill=color)

                # cli and tk interface
                if self.owner == self.player.nickname:
                    print self.headings + "you built an hotel"
                else:
                    print self.other_headings + colored(self.owner.split("_")[0], "cyan", attrs=["bold"]) + " built an hotel"
            
            self.player.unlock("number_of_houses")

            pass
