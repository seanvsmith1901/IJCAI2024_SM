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
T = [] # empty player input vetcor.

# so in my head, either of them can call "get user inputs" or "get current tokens". The only thing that doesn't make sense is updating the tokens.
# ok so what DOES this actually have to do.

# in my head this serves as the communication between the simulation and the server IG, wherein the server will make requests to this fetcher
# and then this fetcher will make requests of the simulator and then can pass that information back
# that way it doesn't matter if we are using the game server or if requests are being made from the GODOT client server thingy
# we cna keep it agnostic that way.
# GOSH I hate GUIS haha
# lets see if I can figure out how T is tabulated.



