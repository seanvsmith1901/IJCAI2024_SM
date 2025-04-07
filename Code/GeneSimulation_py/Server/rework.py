from ServerConnectionManager import ServerConnectionManager
from game_server import GameServer

# See options_creation.py -> group_size_options to understand what this means
SC_GROUP_SIZE = 2

OPTIONS = {
    #General settings
    "NUM_HUMANS": 1,
    "TOTAL_PLAYERS": 5,
    "JHG_ROUNDS_PER_SC_ROUND" : 1,
    "MAX_ROUNDS": 4,
    "SC_GROUP_SIZE": 2
}

OPTIONS["NUM_BOTS"] =  OPTIONS["TOTAL_PLAYERS"] - OPTIONS["NUM_HUMANS"]


# TODO: Check if these are actually needed. I'm not sure what they do...
HEIGHT = 3 # leave this hardcoded for now.
WIDTH = 3
hunters = []


def start_server(host='127.0.0.1', port=12346):
    connection_manager = ServerConnectionManager(host, port, OPTIONS["TOTAL_PLAYERS"], OPTIONS["NUM_BOTS"])
    print("Server started")

    # Halts execution until enough players have joined
    connection_manager.add_clients(OPTIONS["NUM_HUMANS"], OPTIONS["NUM_BOTS"])
    game = GameServer(connection_manager, OPTIONS)
    return connection_manager, game

def start_game(game):
    # Main game loop -- Play as many rounds as specified in OPTIONS
    while game.current_round <= OPTIONS["MAX_ROUNDS"]:
        # This range says how many jhg rounds to play between sc rounds
        for i in range(OPTIONS["JHG_ROUNDS_PER_SC_ROUND"]):
            game.play_jhg_round(game.current_round)
        game.play_social_choice_round(game.sc_round)
        game.sc_round += 1
        game.current_round += 1
        print("New round")

    ### Sean's saving stuff ###
    # game.save_stuff_small()
    # game.save_stuff_big()
    print("game over")


if __name__ == "__main__":
    connection_manager, game = start_server()
    start_game(game)