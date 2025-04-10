from baseagent import AbstractAgent

import numpy as np

class RandomAgent(AbstractAgent):

    def __init__(self):
        super().__init__()
        self.whoami = "random"
        self.pay_taxes = True
        self.gameParams = {}


    def setGameParams(self, gameParams, visualTraits):
        self.gameParams = gameParams


    def play_round(self, player_idx, round_num, recieved, popularities, influence, extra_data):
        tkns = len(popularities) * 2
        tax_tkns = extra_data[0].get('taxes', 0)
        random_vec = np.random.uniform(-1, 1, size=recieved.shape)
        if tax_tkns != 0 or not self.pay_taxes:
            random_vec[0] = 0
        normalized_vec = random_vec / np.linalg.norm(random_vec, ord=1)
        transaction_vec = normalized_vec * (tkns - tax_tkns)
        transaction_vec[0] = tax_tkns if tax_tkns != 0 else transaction_vec[0]
        transaction_vec[player_idx] = np.abs(transaction_vec[player_idx])
        return transaction_vec

