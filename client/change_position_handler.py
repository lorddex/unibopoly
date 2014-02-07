from smart_m3.m3_kp import *
import uuid
import re
import sys
from termcolor import colored
sys.path.append("../")
from sib import SIBLib
import time
import random 
import Tkinter
from client_query import *
from card_handler import *

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

class ChangePositionHandler:
    def __init__(self, player):
        self.player = player
        self.moved_player = None
        self.moved_player_nickname = None
        self.old_position = None
        self.new_position = None
        self.new_position_name = None
        self.gs = None
        self.heading = colored("ChangePositionHandler> ", "blue", attrs=["bold"])
        self.other_heading = colored("ChangePositionHandler> ", "magenta", attrs=["bold"])
        self.interface = self.player.interface
        self.prob_pos = [3, 9, 22, 28]
        
    def handle(self, added, removed):
        
        for i in added:
            self.player.lock("change_position")

            ### USEFUL STUFF ###
            self.old_position = self.player.current_position
            self.moved_player = str(i[0]).split("#")[1]            
            self.moved_player_nickname = self.moved_player.split("_")[0]
            self.gs = self.moved_player.split("_")[1]
            self.new_position = str(i[2]).split("#")[1]
            self.new_position_name = get_position_name(self, self.new_position)
            self.player.current_position = self.new_position
            ##################

            if self.gs == self.player.game_session:
                if self.moved_player == self.player.nickname:
    
                    ##################################################
                    #
                    # Hey, it's me!
                    #
                    ##################################################
    
                    # game session info
                    game_session_status = get_game_session_status(self)
                    
                    if game_session_status == "Active":
                        
                        # debug print 
                        print self.heading + "new position is " + colored(self.new_position_name, "cyan", attrs=["bold"])
                        
                        # Get possible commands
                    
                        # The change position handler is launched when the pawn is positioned for the first time
                        # on the table, and at this time we don't want to show to the user the commands of the box
                        if (int(self.new_position) == 0) & (int(self.player.turn_number) <= 1):
                            self.player.unlock("change_position")
                            pass
    
                        else:
    
                            # get possible commands
                            special_box = ["Imprevisto1", "Imprevisto2", "Probabilita1", "Probabilita2", "Segreteria", "Almawelcome", "Mensa", "Start"]
                            if self.new_position_name in special_box:
                                result = get_possible_commands(self, self.new_position_name)
                            else:
                                gs = self.player.game_session
                                box_name_gs = self.new_position_name + "_" + gs
                                result = get_possible_commands(self, box_name_gs)
    
                            if len(result) > 0:
    
                                # if the command is TakeProbCard or TakeHitchCard
                                # then launch a subscription to read the card value
                                if int(self.new_position) in self.prob_pos:
    
                                    print self.heading + "launching subscription for the extracted card"
                                    
                                    # card sub
                                    self.triple_card = Triple(URI(ns + self.player.game_session),
                                                              URI(ns + "ExtractedCard"),
                                                              None)                                    
                                    self.player.card_st = self.player.node.CreateSubscribeTransaction(self.player.node.ss_handle)
                                    initial_results_card = self.player.card_st.subscribe_rdf(self.triple_card, CardHandler(self))                                
    
                                ##################################################
                                #
                                # Graphical interface part
                                #
                                ##################################################
    
                                if int(self.new_position) > int(self.old_position):
                                    dice = int(self.new_position) - int(self.old_position)
                                    # print str(dice)
                                else:
                                    dice = int(self.new_position) + (37 - int(self.old_position))
                                    
                                if self.player.gtki:
                                    
                                    # Animazione dado
                                    if self.player.last_command == "RollDiceCommand":
                                        for i in range(1,2):
                                            for j in range(1,12):
                                                self.canvas = self.player.interface.canvas
                                                if self.canvas.dadi:
                                                    self.canvas.delete(self.canvas.dadi)
                                                # draw a card
                                                dado = "images/dadi/dado"+ str(j) + ".png"
                                                self.dadi_img = ImageTk.PhotoImage(Image.open(dado))
                                                self.canvas.dadi = self.canvas.create_image(500, 70, image = self.dadi_img, anchor = NW)
                                                time.sleep(0.1)
                                        
                                        # draw a card
                                        self.canvas.delete(self.canvas.dadi)
                                        # dice can be greater than 6 if it's forced
                                        if dice <=6:
                                            dado = "images/dadi/"+ str(dice) + ".png"
                                            # print dado
                                            self.dadi_img = ImageTk.PhotoImage(Image.open(dado))
                                            self.canvas.dadi = self.canvas.create_image(500, 70, image = self.dadi_img, anchor = NW)
                                            # time.sleep(int(dice))
                                        
                                    # moving the piece
                                    if (int(self.old_position)+1) < (int(self.new_position)+1):
                                        pos = range(int(self.old_position) + 1, int(self.new_position)+1)
                                        
                                    else:
                                        # if we are moving after the MoveBackward we use a better way
                                        if int(self.old_position) in self.prob_pos:
                                            pos = range(int(self.old_position) - 1, int(self.new_position)-1, -1)
                                        else:
                                            pos = range(int(self.old_position) + 1, 38) + range(0, int(self.new_position)+1)
    
                                    # print "MOVING PIECE FROM " + str(self.old_position) + " TO " + str(self.new_position)
    
                                    # updating actions in the combobox
                                    
                                    self.interface.actions_combobox_var.set('')
                                    m = self.interface.actions_combobox['menu']
                                    m.delete(0, 'end')
                                    for rs in result:
                                        cmd = rs[0][2].split("#")[1]
                                        m.add_command(label = cmd, command=Tkinter._setit(self.interface.actions_combobox_var, cmd))

                                    # piece animation
                                    for box in pos:
                                        # print str(box)
    
                                        # moving the piece randomizing the positioning into the box
                                        position_randomizer_x = random.randint(-5,5)
                                        position_randomizer_y = random.randint(-5,5)
                                        new_top_x = self.interface.cell_coords[int(box)]['x'] + position_randomizer_x
                                        new_top_y = self.interface.cell_coords[int(box)]['y'] + position_randomizer_y
                                        new_bot_x = new_top_x + 20
                                        new_bot_y = new_top_y + 20
                                        
                                        self.interface.canvas.delete(self.interface.piece)
                                        self.interface.piece = self.interface.canvas.create_oval(
                                            new_top_x, new_top_y, new_bot_x, new_bot_y,
                                            fill = 'yellow', outline = 'black')
    
                                        # updating informations in the label
                                        box_name = get_position_name(self, box)
                                        self.interface.canvas.delete(self.interface.position_editable_label)
                                        self.interface.position_editable_label = self.interface.canvas.create_text(120, 410, text = box_name, anchor = W)

                                        time.sleep(0.3)
    
                                         
                                    # end of graphical user interface part
                                    
                                else:
    
                                    # cli part
                                    
                                    # getting commands
                                    commands = []
                                    commands_id = []
                                    i=0
                                    for rs in result:
                                        print self.heading + "available actions: "
                                        print self.heading + "["+str(i)+"] "+ colored(rs[0][2].split("#")[1], "cyan", attrs=["bold"])
                                        commands.append(rs[0][2].split("#")[1])
                                        commands_id.append(str(i))
                                        i = i + 1
                                        
                                    # waiting for user input
                                    action = None
                                    while not(str(action) in commands_id):
                                        try:
                                            action = input(self.heading + "Action? ")
                                        except Exception:
                                            pass
                                        
                                    print self.heading + "user chose command " + colored(commands[int(action)], "cyan", attrs=["bold"]) + "!"
                                
                                    # building the command triple
                                    triples = []
                                    triples.append(Triple(URI(ns + commands[int(action)]),
                                                          URI(ns + "HasIssuer"),
                                                          URI(ns + self.player.nickname)))
                                    
                                    # Inserting the triple
                                    self.player.node.insert(triples)               
                                    
                else:
    
                    ##################################################
                    #
                    # Has been moved a player other than me
                    #
                    ##################################################
                    
                    print self.other_heading + colored(self.moved_player_nickname, "cyan", attrs=["bold"]) + " is now in position " + colored(self.new_position_name, "cyan", attrs=["bold"])
    
                    ### Graphical interface part
    
                    if self.player.gtki:
                        
                        # getting the new position
                        position_randomizer_x = random.randint(-5,5)
                        position_randomizer_y = random.randint(-5,5)
    
                        new_top_x = self.interface.cell_coords[int(self.new_position)]['x'] + position_randomizer_x
                        new_top_y = self.interface.cell_coords[int(self.new_position)]['y'] + position_randomizer_y
                        new_bot_x = new_top_x + 20
                        new_bot_y = new_top_y + 20
    
                        # getting color
                        if (not (self.interface.pieces_colors.has_key(self.moved_player))):
                            self.interface.pieces_colors[self.moved_player] = random.choice(self.interface.colors)
                            self.interface.colors.remove(self.interface.pieces_colors[self.moved_player])
    
                        # delete the old piece
                        try:
                            self.interface.canvas.delete(self.interface.pieces[self.moved_player])
                        except KeyError:
                            self.interface.pieces[self.moved_player] = None
    
                        # draw the new piece
                        self.interface.pieces[self.moved_player] = self.interface.canvas.create_oval(
                            new_top_x, new_top_y, new_bot_x, new_bot_y,
                            fill = self.interface.pieces_colors[self.moved_player], outline = 'black')
                        
                        # end of graphical interface part
                
            self.player.unlock("change_position")
    
        # triple removal
            
        for i in removed:
            # print "[cph] RIMOSSO " + str(i)
            pass
