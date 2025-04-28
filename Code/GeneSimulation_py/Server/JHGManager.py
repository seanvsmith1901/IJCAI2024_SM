from sim_interface import JHG_simulator


class JHGManager:
    def __init__(self, connection_manager, num_humans, num_players, num_bots):
        self.current_round = 1
        self.connection_manager = connection_manager
        self.num_players = num_players
        self.jhg_sim = JHG_simulator(num_humans, num_players)
        self.num_bots = num_bots

    def play_jhg_round(self, round_num):
        # Occasionally if the JHG round was played to quickly after the SC round, this would catch the SC vote and brick the server.
        # UPDATE: It appears that if the SC submit vote button is spammed quick enough, it would send an additional,
        # unexpected vote. That's the root cause that should get fixed, but this seems to stop it from breaking for now
        while True:
            client_input = self.connection_manager.get_responses()  # Gets responses of type "JHG"

            try:
                first_key = next(iter(client_input))
                client_input[first_key]["ALLOCATIONS"]
                break
            except KeyError:
                print("Error processinging client_input: ", client_input)
        current_popularity = self.jhg_sim.execute_round(client_input, round_num - 1)

        # Creates a 2d array where each row corresponds to the allocation list of the player with the associated id
        allocations_matrix = self.jhg_sim.get_T()

        sent_dict, received_dict = self.get_sent_and_received(allocations_matrix)
        unique_messages = [received_dict, sent_dict]
        self.connection_manager.distribute_message("JHG_OVER", round_num, list(current_popularity),
                                                   self.jhg_sim.get_influence().tolist(), unique_messages=unique_messages)

        self.current_round += 1

        return client_input


    def get_sent_and_received(self, allocations_matrix):
        sent_dict = {}
        received_dict = {}
        bot_offset = self.connection_manager.num_bots

        for client_id in self.connection_manager.clients.keys():
            sent = [0 for _ in range(self.num_players)]
            received = [0 for _ in range(self.num_players)]
            for player in range(self.num_players):
                sent[player] = allocations_matrix[client_id + bot_offset][player]
                received[player] = allocations_matrix[player][client_id + bot_offset]
            sent_dict[client_id] = sent
            received_dict[client_id] = received

        return sent_dict, received_dict