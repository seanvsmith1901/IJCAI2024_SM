# this is just placeholder code its not actually intedned to do anything yet.

import socket
import copy
import select
import json

connected_clients = {}
client_input = {}
client_usernames = {}
HEIGHT = 3 # leave this hardcoded for now.
WIDTH = 3
client_id_dict = {}
hunters = []
MAX_ROUNDS = 2
round = 1
HUMAN_PLAYERS = 2 # start with 2 - I might need to make this dynamic somehow. I'll worry about that later.
T = [] # this is the currently empty player input vector. just store it as empty and we will populate it as necessary.

# so in my head, either of them can call "get user inputs" or "get current tokens". The only thing that doesn't make sense is updating the tokens.
# ok so what DOES this actually have to do.