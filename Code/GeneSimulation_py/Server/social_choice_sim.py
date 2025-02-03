class Social_Choice_Sim:
    def __init__(self, num_players, num_causes):
        self.num_players = num_players
        self.num_causes = num_causes



    def create_nodes(self, options_matrix):
        pass # this is gonna be interesting.
        # we need to take in the matrix
        # are we going to want to keep track of old node positions? who knows. would be server side only though.
        # assuming the options matrix will have 3 options and 11 players
        for player in self.num_players:
            for cause in self.num_causes:
                # how the fetch do we get the position.

                new_vector = options_matrix[player][cause]
