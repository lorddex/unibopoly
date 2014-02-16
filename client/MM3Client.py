from smart_m3.m3_kp import *
import uuid
import re
import sys
from termcolor import colored
sys.path.append("../")
from sib import SIBLib
import time
from client_query import *
# handlers
from turn_handler import TurnHandler
from change_position_handler import ChangePositionHandler
from change_balance_handler import ChangeBalanceHandler
from contract_handler import ContractHandler
from number_of_houses_handler import NumberOfHousesHandler
from game_ended_handler import GameEndedHandler
import threading
import Tkinter
from Tkinter import *
from ttk import *
import os
import signal 
rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

class MM3Client:

    def __init__(self, ip, port, debug, gtki, interface):
        try:
            # client info
            self.gtki = gtki
            self.interface = interface            

            # connection to the sib
            self.node = SIBLib.SibLib(ip, port)
            self.node.join_sib()
            
            # player info
            self.current_position = None
            self.nickname = None
            self.balance = 1000
            self.game_session = None
            self.turn_number = 0            
            self.role = None
            self.waiting = False
            
            self.card_st_on = False    
            self.quit = False

            self.sem_lock = False
            self.semaphore = threading.Lock()
            self.last_command = None
            self.heading = colored("MM3Client> ", "red", attrs=["bold"])

            self.command_available = False

            # board info
            self.properties = []
            for i in range(0,38):
                self.properties.append({})

            print colored("MM3Client>", "red", attrs=["bold"]) + " connected!"
            
        except Exception as e:
            print colored("MM3Client>", "red", attrs=["bold"]) + " Exception while starting the client, aborting!"
            sys.exit(0)

    def lock(self, who):
        if self.sem_lock is False:
            try:
                self.semaphore.acquire()
            except Exception:
                pass
            finally:
                self.sem_lock = True

    def save_command(self, cmd):
        self.command = cmd
        self.command_available = True

    def extract_command(self):
        self.command_available = False
        return self.command    

    def unlock(self, who):
        if self.sem_lock is False: 
            try:
                self.semaphore.release()
            except Exception:
                pass
            finally:
                self.sem_lock = False

    def get_game_session_list(self):

        # query to select available sessions
        query = """
        SELECT ?s
        WHERE {?s ns:HasStatus ns:Waiting}
        """
        result = self.node.execute_query(query)

        game_session_list = []
        for i in result:
            game_session_list.append(str(i[0][2].split('#')[1]))
          
        return game_session_list

    def get_all_game_sessions(self):

        # query to select all sessions
        query = """
        SELECT ?s ?o
        WHERE {?s ns:HasStatus ?o}
        """
        result = self.node.execute_query(query)

        game_session_list = []
        for i in result:
            game_session_list.append(str(i[0][2].split('#')[1]))
        print str(game_session_list)
        return game_session_list
    

    def join_game_session(self, gamesession, role, nickname):
        try:

            # set the role
            self.role = role

            # set the gamesession
            self.game_session = gamesession

            # declare the client as a player or as an observer
            triples = []
            # is nickname already registered?
            player_list = []
            query = """SELECT ?s 
            WHERE {ns:""" + nickname+"_"+str(gamesession) + """ rdf:type ns:Person}"""
            result = self.node.execute_query(query)
            if (len(result) > 0):
                print "Nickname already in use!"                        
                valid = False
            else:
                valid = True

            reg = re.compile(r"[a-zA-Z0-9]*$")
            if not(self.gtki):
                while (valid == False):
                    nickname = raw_input("Insert another nickname > ")
                    while not(reg.match(nickname)):
                        print "Nickname not valid!"
                        nickname = raw_input("Insert another nickname > ")
                    query = """SELECT ?s 
                    WHERE {ns:""" + nickname+"_"+str(gamesession) + """ rdf:type ns:Person}"""
                    result = self.node.execute_query(query)
                    if (len(result) > 0):
                        print "Nickname already in use!"                        
                        valid = False
                    else:
                        valid = True
                               
            # controllo se il nick e' gia' presente (dall'interfaccia grafica)
            else:
                while (valid == False):
                    nickname = self.interface.nickname_entry.get()
                    if len(nickname) > 0:
                        nickname_gs = nickname + "_" + str(gamesession) 
                        query = """SELECT ?s 
                        WHERE {ns:""" + nickname+"_"+str(gamesession) + """ rdf:type ns:Person}"""
                        result = self.node.execute_query(query)
                        if (len(result) > 0):
                            self.interface.error_label2.config(text = ".....Nickname already in use! Insert another one!")#, fill = "red")
                            self.interface.nickname_entry.delete(0, Tkinter.END)
                            self.interface.choose_game_session_button.config(state = NORMAL)
                            self.interface.nickname_entry.config(state = NORMAL)
                            valid = False
                        else:
                            valid = True
                    else:
                        return False
                    
            nickname_gs = nickname + "_" + str(gamesession) 
            self.nickname = nickname_gs
                
            if (role == "player"):
                # get players number for the current session
                temp = []
                query = """
                     SELECT ?s ?o
                     WHERE { ns:""" + gamesession + """ ns:numberOfPlayers ?o}          
                     """

                result = self.node.execute_query(query)
                for i in result:
                    for j in i:
                        for k in j:
                            temp.append(k)

                cont_players=int(temp[5])
                cont_players+=1 
                
                #self.nickname = "player_" + str(cont_players)
    
                # add the player

                # declare the client as a Person
                triples.append(Triple(URI(ns + self.nickname),
                                      URI(rdf + "type"),
                                      URI(ns + "Person")))
                triples.append(Triple(URI(ns + gamesession),
                                      URI(ns + "HasPlayer"),
                                      URI(ns + self.nickname)))
                
                # insert the triples into the sib
                self.node.insert(triples)
                
                # update players number in the sib
                it = []
                dt = []
                it.append(Triple(URI(ns + gamesession),
                                 URI(ns + "numberOfPlayers"),
                                 URI(str(cont_players))))
                                
                dt.append(Triple(URI(ns + gamesession),
                                 URI(ns + "numberOfPlayers"),
                                 URI(str(cont_players - 1))))
            
                self.node.update(it,dt)

                # set the initial position of the player
                triples = []
                triples.append(Triple(URI(ns + self.nickname),
                                      URI(ns + "IsInBox"),
                                      URI(ns + '0')))
                self.current_position = 0

                # set the initial money balance
                triples.append(Triple(URI(ns + self.nickname),
                                      URI(ns + "cashBalance"),
                                      URI("1000")))
                
                triples.append(Triple(URI(ns + self.nickname),
                                      URI(ns + "userID"),
                                      URI(str(cont_players))))

                # insert the triples into the sib
                self.node.insert(triples)
                self.game_session = gamesession
                
            elif (role == "observer"):
#                self.nickname = nickname + "_" + str(gamesession)
                triples.append(Triple(URI(ns + gamesession),
                                      URI(ns + "HasObserver"),
                                      URI(ns + self.nickname)))
                triples.append(Triple(URI(ns + self.nickname),
                                      URI(rdf + "type"),
                                      URI(ns + "Person")))
                # insert the triples into the sib
                self.node.insert(triples)
            return True
        except():
            print colored("MM3Client> ", 'red', attrs=['bold']) + " an exception occurred during the player registration.. aborting!"
            sys.exit(0)

    def launch_subscriptions(self):
        
        # first sub
        triple_turn = Triple(URI(ns + self.game_session),
                        URI(ns + "TurnOf"),
                        None)
        
        print colored("MM3Client> ", 'red', attrs=['bold']) + "new subscription for the turn"        
        self.st1 = self.node.CreateSubscribeTransaction(self.node.ss_handle)
        initial_results1 = self.st1.subscribe_rdf(triple_turn, TurnHandler(self))

        # second sub
        triple_turn = Triple(None,
                        URI(ns + "IsInBox"),
                        None)

        print colored("MM3Client> ", 'red', attrs=['bold']) + "new subscription for the position"        
        self.st2 = self.node.CreateSubscribeTransaction(self.node.ss_handle)
        initial_results2 = self.st2.subscribe_rdf(triple_turn,
            ChangePositionHandler(self))

        # third sub
        triple_balance = Triple(None,
                                URI(ns + "cashBalance"),
                                None)

        print colored("MM3Client> ", 'red', attrs=['bold']) + "new subscription for the cash balance"        
        self.st3 = self.node.CreateSubscribeTransaction(self.node.ss_handle)
        initial_results3 = self.st3.subscribe_rdf(triple_balance, ChangeBalanceHandler(self))

        # fourth sub
        triple_contracts = Triple(None,
                        URI(ns + "HasContract"),
                        None)

        print colored("MM3Client> ", 'red', attrs=['bold']) + "new subscription for the contracts"        
        self.st4 = self.node.CreateSubscribeTransaction(self.node.ss_handle)
        initial_results4 = self.st4.subscribe_rdf(triple_contracts, ContractHandler(self))

        # fifth sub
        triple_houses = Triple(None,
                        URI(ns + "numberOfHouses"),
                        None)

        print colored("MM3Client> ", 'red', attrs=['bold']) + "new subscription for the houses"        
        self.st5 = self.node.CreateSubscribeTransaction(self.node.ss_handle)
        initial_results5 = self.st5.subscribe_rdf(triple_houses, NumberOfHousesHandler(self))

        # sixth sub
        triple_lost = Triple(URI(ns + self.game_session),
                             URI(ns + "HasStatus"),
                             URI(ns + "Ended"))

        print colored("MM3Client> ", 'red', attrs=['bold']) + "new subscription for the end of the game"
        self.st6 = self.node.CreateSubscribeTransaction(self.node.ss_handle)
        initial_results6 = self.st6.subscribe_rdf(triple_lost, GameEndedHandler(self))
        

    def close_subscriptions(self):
        self.lock("MM3Client")
        if self.node is None:
            self.unlock("MM3Client")
            return
        # closing subscriptions
        print colored("MM3Client> ", 'red', attrs=['bold']) + "closing subscriptions..."
        try:
            self.node.CloseSubscribeTransaction(self.st1)
            self.node.CloseSubscribeTransaction(self.st2)
            self.node.CloseSubscribeTransaction(self.st3)
            self.node.CloseSubscribeTransaction(self.st4)
            self.node.CloseSubscribeTransaction(self.st5)
            self.node.CloseSubscribeTransaction(self.st6)
            if self.card_st_on is True:
                self.node.CloseSubscribeTransaction(self.card_st)
        except Exception:
            pass
        self.unlock("MM3Client")

    def force_quit(self):
        self.lock("MM3Client")
        if self.node is None:
            os.kill(os.getpid(), signal.SIGKILL)
#           sys.exit(0)
#            self.unlock("MM3Client")
#            return
        if self.role == "player":    
            try:
                self.quit = True
                if self.game_session is not None:
                    old_balance = get_balance(self)
                    triples_o = []
                    triples_u = []
                    triples_o.append(Triple(URI(ns + self.nickname),
                        URI(ns + "cashBalance"),
                        URI(str(old_balance))))
                    triples_u.append(Triple(URI(ns + self.nickname),
                        URI(ns + "cashBalance"),
                        URI(str(-1))))
                    self.node.update(triples_u, triples_o)
            except AttributeError:
                pass
        else:
            self.close_subscriptions()
            self.leave_sib()
        self.unlock("MM3Client")

    def leave_sib(self):
        self.lock("MM3Client")
        # leaving the sib
        if self.node is None:
            self.unlock("MM3Client")
            return
        print colored("MM3Client> ", 'red', attrs=['bold']) + "leaving the sib..."
        try:
            self.node.leave_sib()
            self.node = None
        except Exception:
            pass
        self.unlock("MM3Client")
    
    def clear_my_sib(self):

        # lock
        self.lock("MM3Client")

        print colored("MM3Client> ", 'red', attrs=['bold']) + "cleaning the sib..."
        # removing all the triples with the loser as the subject
        query = """SELECT ?p ?o WHERE { ns:""" + self.nickname + """ ?p ?o }"""
        s_result = self.node.execute_query(query)
            
        s_triples = []
        for c in s_result:
            s_triples.append(Triple(URI(ns + self.nickname), URI(c[0][2]), URI(c[1][2])))
            if self.node is not None:
                self.node.remove(s_triples)

        # removing all the triples with the loser as the object
        query = """SELECT ?s ?p WHERE { ?s ?p ns:""" + self.nickname + """}"""
        if self.node is not None:
            o_result = self.node.execute_query(query)
        else:
            o_result = []
            
        o_triples = []
        for c in o_result:
            o_triples.append(Triple(URI(c[0][2]), URI(c[1][2]), URI(ns + self.nickname)))
            if self.node is not None:
                self.node.remove(o_triples)
                    
        # unlock
        self.unlock("MM3Client")

    def begin_observer(self):
        # inserting a triple to let the old player observe the rest of the game
        if not(self.node is None):
            obs_triple = [(Triple(URI(ns + self.game_session), URI(ns + "HasObserver"),
                                  URI(ns + self.nickname)))]
            self.node.insert(obs_triple)
            self.role = "observer"
            print self.heading + "now you observe the rest of the match"
            
