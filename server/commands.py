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
from card_commands import *

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

prob = {"DegreePresent": {"action": "card_action_earnall", "param":20},
        "GoToZamboni": {"action": "card_action_goto", "param":29},
        "FreeSandwich": {"action": "card_action_earn", "param":10},
        "GoToAlmaWelcomeAndEarn300": {"action": "card_action_goto_and_earn", "param":[11,300]},
        "GoToBorgoPanigaleStation": {"action": "card_action_goto", "param":15},
        "GoToBusStation": {"action": "card_action_goto", "param":34},
        "GoToCentralStation": {"action": "card_action_goto", "param":5},
        "GoToRefectoryAndEarn100": {"action": "card_action_goto_and_earn", "param":[30,100]},
        "GoToSanVitaleStation": {"action": "card_action_goto", "param":24},
        "InterestingThesis": {"action": "card_action_earn", "param":700},
        "MoveForward1": {"action": "card_action_move_forward", "param":1},
        "MoveForward2": {"action": "card_action_move_forward", "param":2},
        "MoveForward3": {"action": "card_action_move_forward", "param":3},
        "RollDice": {"action": "card_action_rolldice", "param":None},
        "TaxRefund": {"action": "card_action_earn", "param":900}
        }

hitch = {"BirthdayAperitif": {"action":"card_action_payall", "param":10},
         "BuyBook": {"action":"card_action_pay", "param":50},
         "BuyNotebook": {"action":"card_action_pay", "param":500},
         "DegreeParty": {"action":"card_action_pay", "param":200},
         "GoToTerracini": {"action":"card_action_goto", "param":37},
         "GoToSecretary": {"action":"card_action_goto", "param":19},
         "LostBursary": {"action":"card_action_pay", "param":900},
         "LostRoom": {"action":"card_action_pay", "param":200},
         "MoveBackward1": {"action":"card_action_move_backward", "param":1},
         "MoveBackward2": {"action":"card_action_move_backward", "param":2},
         "MoveBackward3": {"action":"card_action_move_backward", "param":3},
         "PayFirstDuty": {"action":"card_action_pay", "param":900},
         "PaySecondDuty": {"action":"card_action_pay", "param":900},
         "PayThirdDuty": {"action":"card_action_pay", "param":300},
         "GoToRefectory": {"action":"card_action_goto", "param":30}
         }


##########################################################
#                                                        #
#                 ROLL DICE COMMAND                      #
#                                                        #
##########################################################
def rolldice(self):
    player = self.server.current_player
    player_id = self.server.current_player_id
     
    # Extract random number
    if self.server.nextdice is not None:
        dices = self.server.nextdice
        self.server.nextdice = None
    else:
        dices = random.randint(1,6)
    
    # Updating player position
    # Get old position
    old_position = get_position(self.server.node, player)
    new_position = int(int(old_position) + dices) % 38
   
    # Get position name
    old_box_name = get_box_name(self, old_position)
    new_box_name = get_box_name(self, new_position)

    # The player earn 300 euro if he passes from start box
    if (int(old_position) > int(new_position)):
        print colored("CommandsHandler> ", "blue", attrs=["bold"]) + player.split("_")[0] + " takes 300 euros passing from the Start"
        earn(self,300)

    # Insert Possible commands
    update_commands(self, player, new_box_name, new_position)

    # Write new position
    ta = [Triple(URI(ns + player),
                 URI(ns + "IsInBox"),
                 URI(ns + str(new_position)))]
    tr = [Triple(URI(ns + player),
                 URI(ns + "IsInBox"),
                 URI(ns + str(old_position)))]
    self.server.node.update(ta, tr)
    
    print colored("CommandHandler> ", "blue", attrs=["bold"]) + "updating " + colored(player.split("_")[0], "cyan", attrs=["bold"]) + " position from " + colored(old_box_name, "cyan", attrs=["bold"]) + " (" + str(old_position) + ")" + " to " + colored(str(new_box_name), "cyan", attrs=["bold"]) + " (" + str(new_position) + ")"
    

##########################################################
#                                                        #
#                      SWITCH TURN                       #
#                                                        #
##########################################################  
def switch_turn(self):

    # Get current player
    old_player = self.server.current_player

    # Get number of players
    self.server.number_of_players = len(get_players(self.server.node, self.server.game_session_id))
    
    # try:
    # Verify if the player has been eliminated or not
    try:
        old_player_id = self.server.players.index(old_player)    
        new_player_id = (old_player_id + 1) % self.server.number_of_players
    except ValueError:
        # il vecchio player e' stato rimosso
        new_player_id = 0
        
    self.server.current_player = self.server.players[new_player_id]
    self.server.current_player_id = new_player_id

    # Updating the triple into the sib
    ta = [Triple(URI(ns + self.server.game_session_id),
                 URI(ns + "TurnOf"),
                 URI(ns + self.server.current_player))]
    tr = [Triple(URI(ns + self.server.game_session_id),
                 URI(ns + "TurnOf"),
                 URI(ns + old_player))]
    self.server.node.update(ta, tr)

    # if self.server.waiting.has_key(old_player):
    #     if self.server.waiting[old_player]:
    #         self.server.waiting[old_player] = False

    # Debug print
    print colored("CommandHandler> ", "blue", attrs=["bold"]) + "it's " + colored(self.server.current_player.split("_")[0], "cyan", attrs=["bold"]) + "'s turn"



##########################################################
#                                                        #
#                      BUY COMMAND                       #
#                                                        #
##########################################################
def buy(self):
    current_player = self.server.current_player
    
    # Get current balance of current player
    old_cash_balance = get_cash_balance(self.server.node, current_player)
    
    # Get position
    position = get_position(self.server.node, current_player)

    # Get position name
    box_name = get_box_name(self, position)

    # Get purchase cost 
    purchaseCost = get_purchase_cost(self, box_name)

    # Update balance
    new_cash_balance = old_cash_balance - purchaseCost
    # if int(new_cash_balance) < 0:
    #     self.server.players.remove(self.server.current_player)
    #     self.server.number_of_players -= 1
    #     t_iib = [Triple(URI(ns + self.server.current_player),
    #                     URI(ns + "IsInBox"),
    #                     URI(ns + str(position)))]
    #     self.server.node.remove(t_iib)

    ta = [(Triple(URI(ns + self.server.current_player),
                          URI(ns + "cashBalance"),
                          URI(ns + str(new_cash_balance))))]
    
    tr = [(Triple(URI(ns + self.server.current_player),
                  URI(ns + "cashBalance"),
                  URI(ns + str(old_cash_balance))))]

    self.server.node.update(ta, tr)

    gs = get_current_gs(self, self.server.current_player)
    box_name_gs = str(box_name) + "_" + gs
    
    # Add contract 
    t = []
    t.append(Triple(URI(ns + self.server.current_player),
                          URI(ns + "HasContract"),
                          URI(ns + box_name_gs)))

    t.append((Triple(URI(ns + box_name_gs),
                          URI(rdf + "type"),
                          URI(ns + "Box"))))

    self.server.node.insert(t)

#TODO settare l'attributo balance del player

##########################################################
#                                                        #
#                     BUILD COMMAND                      #
#                                                        #
##########################################################
def build(self):
    current_player = self.server.current_player
    
    # Get current balance of current player
    old_cash_balance = get_cash_balance(self.server.node, current_player)
    
    # Get position
    position = get_position(self.server.node, current_player)

    # Get position name
    box_name = get_box_name(self, position)

    # Get current game session 
    gs = get_current_gs(self, current_player)
    box_name_gs = str(box_name) + "_" + gs    
     
    # Get purchase cost 
    purchaseCost = get_purchase_cost(self, box_name)

    # Update balance
    new_cash_balance = old_cash_balance - purchaseCost
    # if int(new_cash_balance) < 0:
    #     self.server.players.remove(self.server.current_player)
    #     self.server.number_of_players -= 1
    #     t_iib = [Triple(URI(ns + self.server.current_player),
    #                     URI(ns + "IsInBox"),
    #                     URI(ns + str(position)))]
    #     self.server.node.remove(t_iib)

    ta = [(Triple(URI(ns + self.server.current_player),
                  URI(ns + "cashBalance"),
                  URI(ns + str(new_cash_balance))))]
    
    tr = [(Triple(URI(ns + self.server.current_player),
                  URI(ns + "cashBalance"),
                  URI(ns + str(old_cash_balance))))]    

    self.server.node.update(ta, tr)
    
    # Add contract 
    t = []
    t.append(Triple(URI(ns + self.server.current_player),
                 URI(ns + "HasContract"),
                 URI(ns + box_name_gs)))

    t.append((Triple(URI(ns + box_name_gs),
                          URI(rdf + "type"),
                          URI(ns + "Box"))))

    self.server.node.insert(t)

    old_num_of_houses = get_num_of_houses(self, box_name_gs)
    
    new_num_of_houses = old_num_of_houses + 1

    tr = [(Triple(URI(ns + box_name_gs),
                  URI(ns + "numberOfHouses"),
                  URI(ns + str(old_num_of_houses))))]

    if new_num_of_houses == 4:
        # hotel
        th = [(Triple(URI(ns + box_name_gs),
                      URI(ns + "numberOfHotels"),
                      URI(ns + str(1))))]
        self.server.node.remove(tr)
        self.server.node.insert(th)

    else:
        # houses
        ta = [(Triple(URI(ns + box_name_gs),
                      URI(ns + "numberOfHouses"),
                      URI(ns + str(new_num_of_houses))))]
        self.server.node.update(ta, tr)
        
    # settare l'attributo balance del player

##########################################################
#                                                        #
#                 PAY TO OWNER COMMAND                   #
#                                                        #
##########################################################
def pay_to_owner(self):
    current_player = self.server.current_player
        
    # Get current balance of current player
    my_old_cash_balance = get_cash_balance(self.server.node, current_player)
    
    # Get position of current player
    position = get_position(self.server.node, current_player)

    # Get position name
    box_name = get_box_name(self, position)
    
    # Get current game session
    gs = get_current_gs(self, current_player)
    
    box_name_gs = box_name + "_" + gs

    # Get toll cost of box
    tollCost = get_toll_cost(self, box_name)

    # Get owner of this contract
    owner = get_box_owner(self, box_name_gs)

    # Get cash balance of the owner 
    owner_old_cash_balance = get_cash_balance(self.server.node, owner)
    
    # find the box type
    box_type = get_box_type(self, box_name)
    
    # if it's a society or a station decremente my balance and update the owner's one of tollCost
    if (box_type == "Society") | (box_type == "Station"):

        # Decrease my balance
        my_new_cash_balance = my_old_cash_balance - tollCost
        if int(my_new_cash_balance) < 0:
            self.server.players.remove(self.server.current_player)
            self.server.number_of_players -= 1
            t_iib = [Triple(URI(ns + self.server.current_player),
                            URI(ns + "IsInBox"),
                            URI(ns + str(position)))]
            self.server.node.remove(t_iib)

        ta = [(Triple(URI(ns + self.server.current_player),
                      URI(ns + "cashBalance"),
                      URI(ns + str(my_new_cash_balance))))]
    
        tr = [(Triple(URI(ns + self.server.current_player),
                      URI(ns + "cashBalance"),
                      URI(ns + str(my_old_cash_balance))))]

        self.server.node.update(ta, tr)

        # Increase owner balance
        owner_new_cash_balance = owner_old_cash_balance + tollCost
        
        ta = [(Triple(URI(ns + owner),
                      URI(ns + "cashBalance"),
                      URI(ns + str(owner_new_cash_balance))))]
    
        tr = [(Triple(URI(ns + owner),
                      URI(ns + "cashBalance"),
                      URI(ns + str(owner_old_cash_balance))))]        
        
        self.server.node.update(ta, tr)

        
    # if it's a street decrement my balance and increment the owner's one of tollCost*numberOfHouses
    if (box_type == "Street"):

        # Get number of houses and hotels
        houses = get_num_of_houses(self, box_name_gs)
        hotels = get_num_of_hotels(self, box_name_gs)

        # Multiplier
        if hotels > 0:
            multiplier = 4
        else:
            multiplier = houses

        total_tollCost = tollCost * int(multiplier)
        
        # Decrease my balance
        my_new_cash_balance = my_old_cash_balance - total_tollCost
        if int(my_new_cash_balance) < 0:
            self.server.players.remove(self.server.current_player)
            self.server.number_of_players -= 1
            t_iib = [Triple(URI(ns + self.server.current_player),
                            URI(ns + "IsInBox"),
                            URI(ns + str(position)))]
            self.server.node.remove(t_iib)
        
        ta = [(Triple(URI(ns + self.server.current_player),
                      URI(ns + "cashBalance"),
                      URI(ns + str(my_new_cash_balance))))]
    
        tr = [(Triple(URI(ns + self.server.current_player),
                      URI(ns + "cashBalance"),
                      URI(ns + str(my_old_cash_balance))))]

        self.server.node.update(ta, tr)

        # Increase owner balance
        owner_new_cash_balance = owner_old_cash_balance + total_tollCost
        
        ta = [(Triple(URI(ns + owner),
                      URI(ns + "cashBalance"),
                      URI(ns + str(owner_new_cash_balance))))]
    
        tr = [(Triple(URI(ns + owner),
                      URI(ns + "cashBalance"),
                      URI(ns + str(owner_old_cash_balance))))]        
        
        self.server.node.update(ta, tr)

##########################################################
#                                                        #
#                        EARN                            #
#                                                        #
##########################################################
def earn(self, gain):
    current_player = self.server.current_player

    # Get current balance of current player
    old_cash_balance = get_cash_balance(self.server.node, current_player)
        
    # Update balance
    new_cash_balance = old_cash_balance + gain
    # if int(new_cash_balance) < 0:
    #     self.server.players.remove(self.server.current_player)
    #     self.server.number_of_players -= 1
        
    ta = [(Triple(URI(ns + self.server.current_player),
                  URI(ns + "cashBalance"),
                  URI(ns + str(new_cash_balance))))]

    tr = [(Triple(URI(ns + self.server.current_player),
                  URI(ns + "cashBalance"),
                  URI(ns + str(old_cash_balance))))]

    self.server.node.update(ta, tr)


    
##########################################################
#                                                        #
#                       PAY COMMAND                      #
#                                                        #
##########################################################
def pay(self):
    current_player = self.server.current_player
    # Get current balance of current player
    old_cash_balance = get_cash_balance(self.server.node, current_player)    
        
    # Update balance     
    new_cash_balance = old_cash_balance - 10
    if int(new_cash_balance) < 0:
        self.server.players.remove(self.server.current_player)
        self.server.number_of_players -= 1

        position = get_position(self.server.node, current_player)
        t_iib = [Triple(URI(ns + self.server.current_player),
                        URI(ns + "IsInBox"),
                        URI(ns + str(position)))]
        self.server.node.remove(t_iib)

    ta = [(Triple(URI(ns + self.server.current_player),
                  URI(ns + "cashBalance"),
                  URI(ns + str(new_cash_balance))))]
    
    tr = [(Triple(URI(ns + self.server.current_player),
                  URI(ns + "cashBalance"),
                  URI(ns + str(old_cash_balance))))]

    self.server.node.update(ta, tr)


##########################################################
#                                                        #
#                   UPDATE COMMANDS                      #
#                                                        #
##########################################################
def update_commands(self, player, box_name, new_position):
    # Insert Possible Commands
    
    # if box_name is a street/society/station then actions (to insert
    # for this box into the sib) depend on the actions already executed
    # before by all the players. So the query is used to find the owner 
    # of the box if there isn't an owner then i show all the available 
    # commands as I did before; otherwise if there's an owner, someone 
    # already owns the command. If the current user has the contract I'll
    # leave the triple <box hasPossibleCommand Buy/Build>. If the box is
    # owned by another player, I delete triples <box hasPossibleCommand 
    # buy/build> and insert <box hasPossibleCommand PayToOwnerCommand>

    print colored("CommandHandler> ", "blue", attrs=["bold"]) + "updating possible commands for box " + str(new_position)
    # get current game session
    gs = get_current_gs(self, player)
    box_name_gs = box_name + "_" + gs
    
    # check if the player has to wait
    if self.server.waiting.has_key(self.server.current_player):
        if self.server.waiting[self.server.current_player]:
            
            # remove all the triples "HasPossibleCommands"
            query = """SELECT ?o
            WHERE {ns:""" + box_name_gs + """ ns:HasPossibleCommand ?o }"""
            
            result = self.server.node.execute_query(query)
                        
            if (len(result) > 0):
                triples = []
        
                for i in result:
                    triple = Triple(URI(ns + box_name_gs),
                                    URI(ns + "HasPossibleCommand"),
                                    URI(i[0][2]))
                    triples.append(triple)

                self.server.node.remove(triples)

            # insert a NothingCommand
            t = [Triple(URI(ns+ box_name_gs), 
                        URI(ns + "HasPossibleCommand"), 
                        URI(ns + "NothingCommand"))]            
            self.server.node.insert(t)
                    
            # delete the wait status
            self.server.waiting[self.server.current_player] = False
            
    # find the box type
    box_type = get_box_type(self, box_name)
    if (box_type == "Street") | (box_type == "Society") | (box_type == "Station"):

        purchase_cost = get_purchase_cost(self, box_name)
        player_balance = get_cash_balance(self.server.node, player)
        
        # remove all the triples "HasPossibleCommands"

        query = """SELECT ?o
        WHERE {ns:""" + box_name_gs + """ ns:HasPossibleCommand ?o }"""
        
        result = self.server.node.execute_query(query)
                        
        if (len(result) > 0):
            triples = []
        
            for i in result:
                triple = Triple(URI(ns + box_name_gs),
                                URI(ns + "HasPossibleCommand"),
                                URI(i[0][2]))
                triples.append(triple)

            self.server.node.remove(triples)
            
        if (box_type == "Street"):
            # find the current owner 
            owner = get_box_owner(self, box_name_gs)
            # found someone?
            if (owner is not None): 

                if (owner != player):

                    t = [(Triple(URI(ns + box_name_gs),
                                 URI(ns + "HasPossibleCommand"),
                                 URI(ns + "PayToOwnerCommand")))]
                    self.server.node.insert(t)               

                else:
                    t = []
                    if (player_balance >= purchase_cost):
                        
                        num = int(get_num_of_houses(self, box_name_gs))
                        if num < 3:                                                       
                            t.append(Triple(URI(ns + box_name_gs),
                                            URI(ns + "HasPossibleCommand"),
                                            URI(ns + "BuildCommand")))

                        elif num == 3: 
                            # The owner of the box is the current player.
                            # He already has 3 houses. Now he can built an hotel
                            # only if he owns the other streets of the same colors too.

                            # get all the boxes with the same color of the current position
                            boxes = get_boxes_with_color_same_as(self, box_name)
                            
                            # get the owner of each box selected previously
                            owners = []                
                            for b in boxes:
                                b_gs = b + "_" + gs
                                query = """SELECT ?s
                                WHERE { ?s ns:HasContract ns:""" + b_gs + """ }"""
                                result = self.server.node.execute_query(query)
                                if len(result) > 0:
                                    owners.append(str(result[0][0][2]).split("#")[1])
                                    
                            # check if the owner of the box owns the others boxes too
                            owns_everything = True
                            if len(owners) == len(boxes):
                                for o in owners:
                                    if o != player:
                                        owns_everything = False
                            else:
                                owns_everything = False

                            if owns_everything:
                                t.append(Triple(URI(ns + box_name_gs),
                                                URI(ns + "HasPossibleCommand"),
                                                URI(ns + "BuildCommand")))

                    t.append(Triple(URI(ns+ box_name_gs), 
                                    URI(ns + "HasPossibleCommand"), 
                                    URI(ns + "NothingCommand")))
                    
                    self.server.node.insert(t)

                    
            # else (no-one has the contract of this box)
            else:
                        
                t = []
                if (player_balance >= purchase_cost):

                    t.append(Triple(URI(ns + box_name_gs),
                                    URI(ns + "HasPossibleCommand"),
                                    URI(ns + "BuildCommand")))

                t.append(Triple(URI(ns + box_name_gs), 
                        URI(ns + "HasPossibleCommand"), 
                        URI(ns + "NothingCommand")))

                self.server.node.insert(t)

        elif (box_type == "Station") | (box_type == "Society"):
            # owner = get_box_owner(self, new_position)
            owner = get_box_owner(self, box_name_gs)
            # if someone has this contract I add a PayToOwnerCommand
            if (owner is not None):               
                if (owner != player):
                    t = [(Triple(URI(ns + box_name_gs),
                                 URI(ns + "HasPossibleCommand"),
                                 URI(ns + "PayToOwnerCommand")))]
                    self.server.node.insert(t)               
                
                else:
                    t = [(Triple(URI(ns + box_name_gs),
                                 URI(ns + "HasPossibleCommand"),
                                 URI(ns + "NothingCommand")))]
                    self.server.node.insert(t)                

            # if no-one has this contract I insert BuyCommand
            else:
                t = []
                if (player_balance >= purchase_cost):

                    t.append(Triple(URI(ns + box_name_gs),
                                    URI(ns + "HasPossibleCommand"),
                                    URI(ns + "BuyCommand")))

                t.append(Triple(URI(ns + box_name_gs), 
                        URI(ns + "HasPossibleCommand"), 
                        URI(ns + "NothingCommand")))

                self.server.node.insert(t)

##########################################################
#                                                        #
#                 TAKE CARD COMMAND                      #
#                                                        #
##########################################################

def takecard(self, card_type):

    if (card_type == "hitch"):
        if self.server.nexthitch is None:
            card = random.choice(hitch.keys())
            print "Scelgo a random"
        else:
            print "scelgo la carta " + str(hitch[self.server.nexthitch])
            print str(self.server.nexthitch)
            card = self.server.nexthitch
            self.server.nexthitch = None

        action = hitch[card]["action"]
        param = hitch[card]["param"]
    else:
        if self.server.nextprob in None:
            card = random.choice(prob.keys())
        else:
            card = self.server.nextprob
            self.server.nextprob = None

        action = prob[card]["action"]
        param = prob[card]["param"]

    # insert a triple into the sib
    card_triple = [Triple(URI(ns + self.server.game_session_id),
                          URI(ns + "ExtractedCard"),
                          URI(ns + card))]

    self.server.node.insert(card_triple)

    print colored("CommandHandler> ", "blue", attrs=["bold"]) + "extracted " + colored(card, "cyan", attrs=["bold"]) + ", action: " + action + " with parameter: " + str(param)

    globals()[action](self, param)
