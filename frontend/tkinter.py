#!/usr/bin/python

import random
import uuid
import re
import sys
from termcolor import colored
sys.path.append("../")
from smart_m3.m3_kp import *
from sib import SIBLib
import time
from client import MM3Client 
from Tkinter import *
import Tkinter
from ttk import *
from PIL import ImageTk, Image
import tkFont
from tkMessageBox import showinfo
from client import client_query

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"


class Application(Frame):
     
    def quit_monopoly(self):
        if self.c is not None:
            self.c.force_quit()
        showinfo("Unibopoly v0.1", "Goodbye!")
        self.quit()

    def about_monopoly(self):
        showinfo("Unibopoly v0.1", "Unibopoly v0.1 - Developed by Francesco Apollonio, Alessandra Persano and Fabio Viola")

    def update_gs_list(self):
        if self.role == "player":
            self.gs_list = self.c.get_game_session_list()
        else:
            self.gs_list = self.c.get_all_game_sessions()
        self.gs_tuple = tuple(self.gs_list)

        # filling the combobox
        self.game_sessions_combobox_var.set('Select a game session...')
        m = self.game_sessions_combobox['menu']
        m.delete(0, 'end')
        for gs in self.gs_list:
            m.add_command(label = gs, command=Tkinter._setit(self.game_sessions_combobox_var, gs))

        
    def choose_gs(self):

        self.error_label1.config(text = "")#, fill = "red")
        self.error_label2.config(text = "")#, fill = "red")
        self.error_label3.config(text = "")#, fill = "red")

        # Controlli sul nickname
        reg = re.compile(r"[a-zA-Z0-9]*$")
        nickname = str(self.nickname_entry.get())
                
        if (not(reg.match(nickname)) or len(nickname) == 0) or self.game_sessions_combobox_var.get() == "Select a game session..." or self.role_combobox_var.get() == "Select a role...":
            # self.error_label2.config(text = "Nickname not valid. Insert another one!")#, fill = "red")
            # self.nickname_entry.delete(0, END)
            # self.error_label1.config(text = "Choose a game session!")#, fill = "red")
            # self.error_label3.config(text = "Select a role!")#, fill = "red")
            #return
            
            if not(reg.match(nickname)) or len(nickname) == 0:
                print self.heading + " Nickname not valid!"
                self.error_label2.config(text = "Nickname not valid. Insert another one!")
                # self.error_label1.config(text = "")
                # self.nickname_entry.delete(0, END)
                # self.error_label3.config(text = "")
#                return 
    
            if self.game_sessions_combobox_var.get() == "Select a game session...":
                print self.heading + " Choose a game session!"
                self.error_label1.config(text = "Choose a game session!")
                # self.error_label2.config(text = "")
                # self.error_label3.config(text = "")
                #return
            
#            if self.role_combobox_var.get() == "Select a role...":
#                role = "observer"
#            else:
#                role = self.role_combobox_var.get()

                #print self.heading + " Select a role!"
                #self.error_label3.config(text = "Select a role!")

                # self.error_label2.config(text = "")
                # self.error_label1.config(text = "")
            #return
        
        # join game session
        # try:
        # if self.c.join_game_session(self.game_sessions_combobox_var.get(), "player", self.nickname_entry.get()) == False:

        if self.c.join_game_session(self.game_sessions_combobox_var.get(), self.role, self.nickname_entry.get()) == False:
            return
        
        # except Exception:
        #     print "Choose a game session!"
        #     self.error_label1.config(text = "Choose a valid game session!", fg = "red")

        # launch subscriptions

        # piece
        if self.role == "player":
            position_randomizer_x = random.randint(-15,15)
#            position_randomizer_y = random.randint(-5,5)
        
            new_top_x = self.cell_coords[0]['x'] + position_randomizer_x
            new_top_y = self.cell_coords[0]['y'] - 8
       
            new_bot_x = new_top_x + 13
            new_bot_y = new_top_y + 13
        
            self.piece = self.canvas.create_oval(new_top_x, new_top_y, new_bot_x, new_bot_y, fill = 'yellow')

        self.c.launch_subscriptions()
         
        # disable button and combobox for the game sessions
        self.update_game_session_button.config(state = DISABLED)
        self.choose_game_session_button.config(state = DISABLED)
        self.game_sessions_combobox.config(state = DISABLED)
        self.role_combobox.config(state = DISABLED)
 
        # disable username field
        self.nickname_entry.config(state = DISABLED)

                       
    def choose_action(self):
        action = self.actions_combobox_var.get()

        if action == "":
            return

        print self.heading + " Action chosen: " + action

        self.c.last_command = action

        # build the triple
        t = [Triple(URI(ns + action),
                    URI(ns + "HasIssuer"),
                    URI(ns + self.c.nickname))]
    
        # insert the triple
        self.c.node.insert(t)

        # empty combobox
        try:
            m = self.actions_combobox.children['menu']
            m.delete(0, 'end')
        except Exception:
            pass
        self.actions_combobox_var.set('Select an action...')

    def connect(self):

        # MM3Client
        self.c = MM3Client.MM3Client(self.ip_entry.get(), int(self.port_entry.get()), True, True, self)
        self.role = self.role_combobox_var.get()               
        if self.role == "Select a role..":
            self.role = "observer"
        
        # getting game session list
        if self.role == "player":
            self.gs_list = self.c.get_game_session_list()
        else:
            self.gs_list = self.c.get_all_game_sessions()

        self.gs_tuple = tuple(self.gs_list)

        # filling the combobox
        self.game_sessions_combobox_var.set('Select a game session...')
        m = self.game_sessions_combobox['menu']
        m.delete(0, 'end')
        for gs in self.gs_list:
            m.add_command(label = gs, command=Tkinter._setit(self.game_sessions_combobox_var, gs))

        # enable choose_game_session_button and update_game_session_button
        self.update_game_session_button.config(state = NORMAL)
        self.choose_game_session_button.config(state = NORMAL)

        # disable connection fields
        self.ip_entry.config(state = DISABLED)
        self.port_entry.config(state = DISABLED)
        self.connect_button.config(state = DISABLED)
        self.role_combobox.config(state = DISABLED)

    def createWidgets(self):

        # Frames 
        self.connection_frame = Frame(self)
        self.connection_frame.pack() #padx = 10, pady = 10)

        self.game_sessions_frame = Frame(self)
        self.game_sessions_frame.pack() #padx = 10, pady = 10)

        self.labels_frame = Frame(self)
        self.labels_frame.pack()

        self.actions_frame = Frame(self)
        self.actions_frame.pack()

        self.buttons_frame = Frame (self)
        self.buttons_frame.pack(side = BOTTOM, pady=10)

        # Action Label
        self.choose_action_label = Label(self.actions_frame, text="Choose action:", width=12)
        self.choose_action_label.pack( side = LEFT )        

        # Action Combobox
        self.actions_combobox_var = StringVar(self.actions_frame)
        self.actions_combobox_items = ()
        self.actions_combobox = OptionMenu(self.actions_frame, self.actions_combobox_var, self.actions_combobox_items)
        self.actions_combobox.config( state = DISABLED, width = 20 )
        self.actions_combobox.pack(side = LEFT)
        self.actions_combobox_var.set('Select an action...')
        
        # Choose Action Button
        self.choose_action_button = Button(self.actions_frame)
        self.choose_action_button["text"] = "Choose Action"
#        self.choose_action_button["fg"]   = "black"
        self.choose_action_button["command"] =  self.choose_action
        self.choose_action_button.config( state = DISABLED )
        self.choose_action_button.pack( side = LEFT)        

        # Turn label
        self.turn_label = Label(self.actions_frame, text="Current player: ")
        self.turn_label.pack( side = LEFT )

        self.turn_editable_label = Label(self.actions_frame, text="-")
        self.turn_editable_label.pack( side = LEFT )

        # IP Label
        self.ip_label = Label(self.connection_frame, text="IP")
        self.ip_label.pack(side = LEFT)
        self.ip_entry = Entry(self.connection_frame)
        self.ip_entry.pack(side = LEFT)
        self.ip_entry.insert(0, "localhost")

        # Port Label
        self.port_label = Label(self.connection_frame, text="Port")
        self.port_label.pack(side = LEFT)
        self.port_entry = Entry(self.connection_frame)
        self.port_entry.pack(side = LEFT)
        self.port_entry.insert(0, "10010")
        self.port_entry.config(width = 7)

        # Role Combobox
        self.role_combobox_var = StringVar(self.connection_frame)
        self.role_combobox_items = ()
        self.role_combobox = OptionMenu(self.connection_frame, self.role_combobox_var, self.role_combobox_items)
#        self.role_combobox.grid( row=1, column=2, sticky = W, padx=10 )
        self.role_combobox.pack(side = LEFT, padx = 15, pady = 5)
        self.role_combobox.config(width = 10)
        self.role_combobox_var.set('Select a role...')
        r = self.role_combobox['menu']
        r.delete(0, 'end')
        r.add_command(label = "player", command=Tkinter._setit(self.role_combobox_var, "player"))
        r.add_command(label = "observer", command=Tkinter._setit(self.role_combobox_var, "observer"))

        # Connect Button
        self.connect_button = Button(self.connection_frame)
        self.connect_button["text"] = "Connect"
#        self.connect_button["fg"]   = "black"
        self.connect_button["command"] =  self.connect
        self.connect_button.pack(side = LEFT, padx = 15, pady = 5)

        # Nickname Label
        self.nickname_label = Label(self.game_sessions_frame, text="Insert a nickname")
        self.nickname_label.grid( row = 1, sticky = W)

        # Nickname entry
        self.nickname_entry = Entry(self.game_sessions_frame)
        self.nickname_entry.grid(row=1, column=1, sticky = W)
       
        # Error Labels
        self.error_label1 = Label(self.game_sessions_frame, text=" ")
        self.error_label1.grid( row = 2, column = 1 )        
        self.error_label2 = Label(self.game_sessions_frame, text=" ")
        self.error_label2.grid( row = 3, column = 1 )        
        self.error_label3 = Label(self.game_sessions_frame, text=" ")
        self.error_label3.grid( row = 3, column = 2 )        

        
        # Game session Label
        self.gs_label = Label(self.game_sessions_frame, text="Choose game session")
        self.gs_label.grid( row=0 , sticky = W)      

        # Game Session Combobox
        self.game_sessions_combobox_var = StringVar(self.game_sessions_frame)
        self.game_sessions_combobox_items = ()
        self.game_sessions_combobox = OptionMenu(self.game_sessions_frame, self.game_sessions_combobox_var, self.game_sessions_combobox_items)
        self.game_sessions_combobox.grid( row=0, column=1, sticky = W, padx=10 )
        self.game_sessions_combobox.config(width = 35)
        self.game_sessions_combobox_var.set('Select a game session...')
        
        # Update Game Session Button
        self.update_game_session_button = Button(self.game_sessions_frame)
        self.update_game_session_button["text"] = "Update"
        self.update_game_session_button["command"] =  self.update_gs_list
        self.update_game_session_button.config(state = DISABLED)
        self.update_game_session_button.grid( row=0,column=2, sticky = W )
        
        # Choose Game Session Button
        self.choose_game_session_button = Button(self.game_sessions_frame)
        self.choose_game_session_button["text"] = "Enter"
        self.choose_game_session_button["command"] =  self.choose_gs
        self.choose_game_session_button.config(state = DISABLED)
        self.choose_game_session_button.grid( row=1,column=3, sticky = W )

        # canvas
        self.canvas = Canvas(self.labels_frame, width = 651, height = 490)
        self.canvas.pack(side = BOTTOM, padx = 10, pady = 3)
        self.canvas.config(bd = 0, highlightthickness= 0)
        self.canvas.dadi = None

        # board
        self.img = ImageTk.PhotoImage(Image.open("images/tabellone1.png"))
        self.canvas.create_image(0, 0, image = self.img, anchor = NW)

        # balance
        self.canvas.create_text(90, 390, text = "Balance: ")
        self.balance_editable_label = self.canvas.create_text(120, 390, text = "-")

        # position
        self.canvas.create_text(90, 410, text = "Position: ")
        self.position_editable_label = self.canvas.create_text(120, 410, text = "-")

        # Info Button
        self.Info = Button(self.buttons_frame)
        self.Info["text"] = "About"
#        self.Info["fg"]   = "black"
        self.Info["command"] =  self.about_monopoly
        self.Info.pack( side = LEFT )

        # Quit Button
        self.Quit = Button(self.buttons_frame)
        self.Quit["text"] = "Quit"
        self.Quit.foreground = "black"
        self.Quit["command"] =  self.quit_monopoly
        self.Quit.pack( side = LEFT )

    def __init__(self, master=None):
        self.s = Style()
        self.s.theme_use('clam')
        self.cell_coords = []
        self.pieces = {}
        self.pieces_colors = {}
        self.colors = ["white", "red", "green", "blue", "cyan", "magenta"]
        self.houses = {}
        self.c = None
        ### boxes' center coordinates
        
        self.heading = colored("TkClient> ", "grey", attrs=["bold"])
    
        # bottom side
        x = 613.7
        y = 452.7
        for i in range(0, 12):
            self.cell_coords.append({"x":x, "y":y})
            x = x - 53.4

        # left side
        x = 26.3
        y = 452.7
        for i in range(12, 19):
            y = y - 53.4
            self.cell_coords.append({"x":x, "y":y})

        # top side
        x = 26.3
        y = 26.3
        for i in range(19, 31):
            self.cell_coords.append({"x":x, "y":y})
            x = x + 53.4

        # right side
        x = 613.7
        y = 26.3
        for i in range(31, 38):
            y = y + 53.4
            self.cell_coords.append({"x":x, "y":y})

        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

root = Tk()
root.wm_title("Unibopoly v0.1")
app = Application(master=root)
app.mainloop()
root.destroy()
