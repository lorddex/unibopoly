from server import MM3Server
import sys

if len(sys.argv) < 4: 
    print "Wrong number of arguments! You should use:"
    print "$ python server.py server_ip server_port number_of_players"
    sys.exit(0)

s = MM3Server.MM3Server(sys.argv[1], int(sys.argv[2]), True)
s.new_game_session(int(sys.argv[3]))
s.launch_subscriptions()

print "CTRL+D to close\n"
while True:
    try:
        cmd = raw_input('> ')
        if cmd is not "":
            s.parse_command(cmd)
    except EOFError:
        print "Bye"
        s.close_gamesession()
        sys.exit(0)
