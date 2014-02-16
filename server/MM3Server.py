from smart_m3.m3_kp import *
from termcolor import colored
import uuid
import sys
sys.path.append("../")
from sib import SIBLib
import random
from activate_game_session_handler import ActivateGameSessionHandler
from command_handler import CommandHandler
from game_ended_handler import GameEndedHandler
import threading
from query import get_players, get_cash_balance

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

class MM3Server():

    def __init__(self, ip, port):
        try:
            # connection to the sib
            self.node = SIBLib.SibLib(ip, port)
            self.node.join_sib()

            # game informations
            self.game_session_id = None
            self.current_player = None
            self.current_player_id = None
            self.players = []
            self.number_of_players = 0
            self.required_players = None
            self.turn_number = 1
            self.sem_lock = False
            self.waiting = {}
            self.semaphore = threading.Lock()
            self.nextdice = None 
            self.nexthitch = None
            self.nextprob = None
            self.heading = colored("MM3Server> ", 'green', attrs=['bold']) 

            print self.heading + "joining the sib on " + ip + ":" + str(port)

        except():
            print self.heading + " an exception occurs during the creation of the server, aborting!"
            sys.exit(0)

    def lock(self):
        if self.sem_lock is False:
            try: 
                self.semaphore.acquire()
            except Exception:
                pass
            finally:
                self.sem_lock = True

    def unlock(self):
        if self.sem_lock is True:
            try:
                self.semaphore.release()
            except Exception:
                pass
            finally:
                self.sem_lock = False
    
    def clean_my_sib(self):
        self.lock()
        print self.heading + "cleaning the sib..."
        query = """SELECT ?s ?p ?o WHERE { ?s ?p ?o }"""
        result = self.node.execute_query(query)
        triples = []
        for i in result:
            if len(i)>0 and len(i[0])>0 and len(str(i[0][2]).split("_"))>1:
                if self.game_session_id == str(i[0][2]).split("_")[1]:
                    triples.append(Triple(URI(i[0][2]), URI(i[1][2]), URI(i[2][2])))
        self.node.remove(triples)
        self.unlock() 
            
    def leave_sib(self):
        self.lock()
        print self.heading + "leaving the sib..."
        self.clean_my_sib()
        self.node.leave_sib()
        self.unlock()

    def parse_command(self, cmd):
        parms = []
        if len(cmd) > 1:
            for a in cmd.split(" ")[1:]:
                parms.append(a)
        action = cmd.split(" ")[0]
        
        # this action modifies the player's balance
        if action == "balance" and len(parms) == 2:
            players = get_players(self.node, self.game_session_id)
            nick = parms[0] + "_" + self.game_session_id
            if nick in players:
                triples_u = []     
                triples_o = []
                old_balance = get_cash_balance(self.node, nick)
                triples_o.append(Triple(URI(ns + nick),
                                        URI(ns + "cashBalance"),
                                        URI(ns + str(old_balance))))
                triples_u.append(Triple(URI(ns + nick),
                                        URI(ns + "cashBalance"),
                                        URI(ns + str(parms[1]))))
                self.node.update(triples_u, triples_o)
                print self.heading + " player " + parms[0]  + " has now " + str(get_cash_balance(self.node, nick))

        # this action alters the dice for the next turn
        elif action == "nextdice" and len(parms) == 1:
            self.nextdice=int(parms[0])

        elif action == "nexthitch" and len(parms) == 1:
            self.nexthitch=parms[0]
            
        elif action == "nextprob" and len(parms) == 1:
            self.nextprob=parms[0]
                    
    def new_game_session(self, required_players):

        # simply create a triple in the sib to define a new GameSession
        self.required_players = required_players
        self.game_session_id = str(uuid.uuid4())

        # creation of the new game session
        triples = []     

        triples.append(Triple(URI(ns +  self.game_session_id),
                              URI(rdf + "type"),
                              URI(ns + "GameSession")))

        # setting the state for the new game session
        triples.append(Triple(URI(ns + self.game_session_id),
                              URI(ns + "HasStatus"),
                              URI(ns + "Waiting")))

        # setting the number of player for the game session
        triples.append(Triple(URI(ns + self.game_session_id),
                              URI(ns + "numberOfPlayers"),
                              URI(ns + "0")))

        # inserting the triples into the sib
        self.node.insert(triples)
        
        print self.heading + "new game session with id " + colored(self.game_session_id, "cyan", attrs=["bold"])
        print self.heading + "inserting a triple for the new GameSession into the sib"
        print self.heading + "inserting a triple for the state of the new GameSession into the sib"
        print self.heading + "inserting a triple for the number of players for the new GameSession"

        # game session activation
        triple = Triple(URI(ns + self.game_session_id),
                        URI(ns + "numberOfPlayers"),
                        URI(ns + str(required_players)))


        print self.heading + "new subscription to check the number of players (" + str(required_players) + ")"

        self.ags_st = self.node.CreateSubscribeTransaction(self.node.ss_handle)
        initial_results_ags = self.ags_st.subscribe_rdf(triple, ActivateGameSessionHandler(self))

        # returning the game session id
        return self.game_session_id


    # put inside this method all the functions required for be launched before closing the server
    def close_gamesession(self):

        triples = []
        for i in get_players(self.node, self.game_session_id):
            triples.append(Triple(URI(ns + i), None, None))
            triples.append(Triple(None, None, URI(ns + i)))
        self.node.remove(triples)

        triples = []
        # cleanup
        triples.append(Triple(URI(ns +  self.game_session_id),
                              URI(rdf + "type"),
                              URI(ns + "GameSession")))
        # setting the state for the new game session
        triples.append(Triple(URI(ns + self.game_session_id),
                              URI(ns + "HasStatus"),
                              None))
        # setting the number of player for the game session
        triples.append(Triple(URI(ns + self.game_session_id),
                              URI(ns + "numberOfPlayers"),
                              None))
        self.node.remove(triples)

        self.close_subscriptions()
        self.leave_sib()


    def launch_subscriptions(self):

        # command subscription
        triple = Triple(None,
                        URI(ns + "HasIssuer"),
                        None)

        print self.heading + "new subscription to check the received commands"

        self.c_st = self.node.CreateSubscribeTransaction(self.node.ss_handle)
        initial_results_c = self.c_st.subscribe_rdf(triple, CommandHandler(self))

        # game ended subscription
        ge_triple = Triple(URI(ns + self.game_session_id),
                        URI(ns + "HasPlayer"),
                        None)

        print self.heading + "new subscription to check the end of the game"

        self.ge_st = self.node.CreateSubscribeTransaction(self.node.ss_handle)
        initial_results_ge = self.ge_st.subscribe_rdf(ge_triple, GameEndedHandler(self))

    def close_subscriptions(self):
        
        # closing subscriptions
        print self.heading + "closing subscriptions..."
        try:
            self.node.CloseSubscribeTransaction(self.c_st)
            self.node.CloseSubscribeTransaction(self.ags_st)
            self.node.CloseSubscribeTransaction(self.ge_st)
        except Exception:
            pass
