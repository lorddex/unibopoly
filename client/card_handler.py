import os
from client_query import *
import random
import uuid
import re
import sys
from termcolor import colored
sys.path.append("../")
from smart_m3.m3_kp import *
from sib import SIBLib
import time
import MM3Client 
from Tkinter import *
import Tkinter
from PIL import ImageTk, Image
import tkFont
from tkMessageBox import showinfo

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

class CardHandler:
    def __init__(self, prev_handler):
        self.prev_handler = prev_handler
        self.heading = colored("CardHandler> ", "blue", attrs=["bold"])
        
    def handle(self, added, removed):
        
        for i in added:
            self.prev_handler.player.lock("card")
            card = self.extracted_card = str(i[2]).split("#")[1]
            print self.heading + " extracted card: " + colored(card, "cyan", attrs=["bold"])

            # check if the extracted card is related to secretary
            if card == "GoToSecretary":
                print "locking the next round"
                self.prev_handler.player.waiting = True

            # removing subscription
            print self.heading + "removing subscription for the extracted card"
            self.prev_handler.player.node.CloseSubscribeTransaction(self.prev_handler.player.card_st)
            self.prev_handler.player.card_st_on = False
            
            # removing the triple
            self.prev_handler.player.node.remove(self.prev_handler.triple_card)

            # graphical user interface part
            if self.prev_handler.player.gtki:

                # get card image filename
                card_name = "../frontend/images/" + card + ".png"
                abs_card_name = os.path.abspath(card_name)
                print abs_card_name

                # draw a card
                self.canvas = self.prev_handler.player.interface.canvas
                self.card_img = ImageTk.PhotoImage(Image.open(abs_card_name))
                self.canvas.card = self.canvas.create_image(200, 200, image = self.card_img, anchor = NW)
                time.sleep(5)
                self.canvas.delete(self.canvas.card)
            self.prev_handler.player.unlock("card")
            
        for i in removed:
            pass
