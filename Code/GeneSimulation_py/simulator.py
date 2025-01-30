from .engine import JHGEngine




# from what I was able to gather, I need to make this a proxy object - so we have the server and whatnot getting routed through here.

class GameSimulator:

    def __init__(self, game_params) -> None:
        # all of the client information that we are going to need
        self.engine = JHGEngine(**game_params)
        self.extra_data = {
            i: {
                j: None for j in range(self.engine.N)
            } for i in range(self.engine.N)
        }

    def get_influence(self):
        return self.engine.get_influence()

    def get_prev_influence(self):
        return self.engine.get_prev_influence()

    def get_popularity(self):
        return self.engine.get_popularity()

    def get_transaction(self):
        return self.engine.get_transaction()

    def get_extra_data(self, player_id):
        return self.extra_data[player_id]

    def set_extra_data(self, sender_id, reciever_id, data):
        self.extra_data[reciever_id][sender_id] = data

    def play_round(self, T):
        self.engine.apply_transaction(T)

    def save(self, outFilePath):
        with open(outFilePath, "w") as f:
            param_col_str = f"round,alpha,beta,give,keep,steal"
            pops_col_str = ",".join(f'p{i}' for i in range(len(self.engine.get_popularity())))
            act_col_str = ",".join(f'p{i}=>p{j}' for i in range(len(self.engine.get_popularity())) for j in range(len(self.engine.get_popularity())))
            f.write(f"{param_col_str},{pops_col_str},{act_col_str}\n") # column names
            for t in range(self.engine.t+1):
                param_str = f"{t},{self.engine.alpha},{self.engine.beta},{self.engine.C_g},{self.engine.C_k},{self.engine.C_s}"
                pops_str = ",".join(f'{p}' for p in self.engine.get_popularity(t))
                act_str = ",".join(f'{a}' for a in self.engine.get_transaction(t).flatten())
                f.write(f"{param_str},{pops_str},{act_str}\n")






