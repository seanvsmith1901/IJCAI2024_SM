from JHGManager import JHGManager
from SCManager import SCManager
from ServerConnectionManager import ServerConnectionManager


OPTIONS = {
    #General settings
    "NUM_HUMANS": 1,
    "TOTAL_PLAYERS": 5,
    "JHG_ROUNDS_PER_SC_ROUND" : 1,
    "MAX_ROUNDS": 1000,
    "SC_GROUP_OPTION": 2, # See options_creation.py -> group_size_options to understand what this means
    "SC_VOTE_CYCLES": 3
}
OPTIONS["NUM_BOTS"] =  OPTIONS["TOTAL_PLAYERS"] - OPTIONS["NUM_HUMANS"]


class Server():
    def __init__(self, options):
        self.connection_manager = None
        self.num_players = options["TOTAL_PLAYERS"]
        self.num_humans = options["NUM_HUMANS"]
        self.num_bots = options["NUM_BOTS"]
        self.sc_group_option = options["SC_GROUP_OPTION"]
        self.jhg_rounds_per_sc_round = options["JHG_ROUNDS_PER_SC_ROUND"]
        self.max_rounds = options["MAX_ROUNDS"]
        self.sc_vote_cycles = options["SC_VOTE_CYCLES"]


    def start_server(self, host='127.0.0.1', port=12346):
        self.connection_manager = ServerConnectionManager(host, port, OPTIONS["TOTAL_PLAYERS"], OPTIONS["NUM_BOTS"])
        self.JHG_manager = JHGManager(self.connection_manager, self.num_humans, self.num_players, self.num_bots)
        self.SC_manager = SCManager(self.connection_manager, self.num_humans, self.num_players, self.num_bots,
                                    self.sc_group_option, self.sc_vote_cycles)
        print("Server started")

        # Halts execution until enough players have joined
        self.connection_manager.add_clients(OPTIONS["NUM_HUMANS"], OPTIONS["NUM_BOTS"], OPTIONS["SC_VOTE_CYCLES"])


    def play_game(self):
        # Main game loop -- Play as many rounds as specified in OPTIONS
        self.SC_manager.init_next_round()
        while self.JHG_manager.current_round <= self.max_rounds:
            for i in range(self.jhg_rounds_per_sc_round): # This range says how many jhg rounds to play between sc rounds
                self.JHG_manager.play_jhg_round(self.JHG_manager.current_round)
            self.SC_manager.play_social_choice_round()
            print("New round")

        print("game over")


if __name__ == "__main__":
    server = Server(OPTIONS)
    server.start_server()
    server.play_game()