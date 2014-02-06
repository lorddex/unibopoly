#!/usr/bin/python

from server.MM3Server import *
from sib.SIBLib import *
from user.UserLib import *
import time

s = MM3Server("localhost", 10010, True)
sess_id = s.new_game_session(2)
s.activate_game_session(sess_id, 2)

print "CTRL+D to close\n"
while True:
    try:
        cmd = raw_input('> ')
        if s is not "":
            s.execute_cmd(cmd)
    except EOFError:
        print "Bye"
        # TODO: Clean UP
        s.close_gamesession()
        sys.exit(0)
