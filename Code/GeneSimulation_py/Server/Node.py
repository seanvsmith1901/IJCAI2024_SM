class Node:
    def __init__(self, x_pos, y_pos, type, text):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.type = type
        self.text = text


    def calc_position(self, x_list, y_list):
        pass # take in all of the x and y positions and sum it into its new x and y position

    def get_x(self):
        return self.x_pos

    def get_y(self):
        return self.y_pos

    def __str__(self):
        return self.x_pos, ", ", self.y_pos, " ", self.type, " ", self.text, "\n"

    def to_json(self):
        return { # make these json freindly please. all of these are strings or floats, instead of custom objects.
            "type": self.type,
            "text": self.text,
            "x_pos": self.x_pos,
            "y_pos": self.y_pos,
        }
