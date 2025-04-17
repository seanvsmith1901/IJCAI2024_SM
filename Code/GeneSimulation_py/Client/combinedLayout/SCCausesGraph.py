from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from combinedLayout.colors import COLORS

from combinedLayout.Arrow import Arrow


class SCCausesGraph(QWidget):
    def __init__(self):
        super().__init__()

        self.nodes_fig = Figure(figsize=(5, 4), dpi=100)
        self.nodes_ax = self.nodes_fig.add_subplot(111)
        self.nodes_canvas = FigureCanvas(self.nodes_fig)
        self.nodes_dict = {}
        self.arrows = {}
        self.nodes_type = []
        self.nodes_text = []
        self.nodes_x = []
        self.nodes_y = []
        self.round_state = None

        layout = QVBoxLayout()
        layout.addWidget(self.nodes_canvas)
        self.setLayout(layout)


    def init_sc_nodes_graph(self, round_state):
        self.round_state = round_state

        # Set background colors
        self.nodes_fig.patch.set_facecolor("#282828ff")
        self.nodes_ax.set_facecolor("#282828ff")

        # Hide ticks and tick labels
        self.nodes_ax.set_xticks([])
        self.nodes_ax.set_yticks([])
        self.nodes_ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

        # Hide spines by setting their color to match background
        for spine in self.nodes_ax.spines.values():
            spine.set_color("#282828")

        # Turn off the grid and clear any pre-existing content
        self.nodes_ax.grid(False)
        self.nodes_ax.cla()
    
    
    def update_sc_nodes_graph(self, round_num, winning_vote=None):
        if self.round_state.nodes:
            # Clear graph
            self.nodes_ax.cla()
            self.arrows.clear()
            self.nodes_x.clear()
            self.nodes_y.clear()
            self.nodes_type.clear()
            self.nodes_text.clear()

            # Update node data
            for node in self.round_state.nodes[round_num]:
                mini_dict = {"x_pos": float(node["x_pos"]), "y_pos": float(node["y_pos"])}
                self.nodes_dict[node["text"]] = mini_dict
                self.nodes_x.append(float(node["x_pos"]))
                self.nodes_y.append(float(node["y_pos"]))
                self.nodes_type.append(node["type"])
                self.nodes_text.append(node["text"])

            colors = []

            # Update or add annotations to the axes
            if winning_vote:
                winning_vote += 1

            for i, (x_val, y_val) in enumerate(zip(self.nodes_x, self.nodes_y)):
                text = self.nodes_text[i]
                if text.startswith("Player"):
                    split_string = text.split()
                    text = split_string[1]
                    color = COLORS[int(split_string[1]) - 1]
                elif text == "Cause " + str(winning_vote):
                    color = "#e41e1e"  # red
                else:
                    color = "#EBEBEB"

                # If an annotation already exists, update it; otherwise, create a new one
                annotations = [ann for ann in self.nodes_ax.texts if ann.get_text() == text]
                if annotations:
                    # Update existing annotation
                    annotations[0].set_position((x_val, y_val))
                    annotations[0].set_color(color)
                else:
                    # Create new annotation
                    self.nodes_ax.annotate(
                        text,
                        (x_val, y_val),
                        textcoords="offset points",
                        xytext=(0, 3),
                        ha='center',
                        fontsize=9,
                        color=color,
                        weight='bold',
                        zorder=587,
                    )

                colors.append(color)

            self.nodes_ax.text(
                0.98, 0.98,  # near top-right corner
                f"Round {round_num}",
                transform=self.nodes_ax.transAxes,
                ha='right',
                va='top',
                fontsize=10,
                color='white',
                weight='bold',
                zorder=10,
            )

            self.nodes_ax.scatter(self.nodes_x, self.nodes_y, marker='o', c=colors)

            max_x = max(abs(x) for x in self.nodes_x)
            max_y = max(abs(y) for y in self.nodes_y)
            max_range = max(max_x, max_y) + 1  # Add some padding if you like

            self.nodes_ax.set_xlim(-max_range, max_range)
            self.nodes_ax.set_ylim(-max_range, max_range)

            self.nodes_ax.set_aspect('equal', adjustable='box')

            # Redraw the canvas
            self.nodes_canvas.draw()


    def update_arrows(self, potential_votes):
        # checks for existing arrows, and removes them.
        if potential_votes:  # only run this if there are actual potential votes.
            for arrow in self.arrows:  # if there is anything in there.
                arrow.remove()

            self.arrows = []  # clean the arrows array.
            for key in potential_votes:
                if int(potential_votes[key]) != -1:
                    player_name = "Player " + str(int(key) + 1)
                    start_x = self.nodes_dict[player_name]["x_pos"]
                    start_y = self.nodes_dict[player_name]["y_pos"]
                    cause_name = "Cause " + str(int(potential_votes[key]))
                    end_x = self.nodes_dict[cause_name]["x_pos"]
                    end_y = self.nodes_dict[cause_name]["y_pos"]

                    new_arrow = Arrow((start_x, start_y), (end_x, end_y), color=COLORS[int(key)])
                    self.arrows.append(new_arrow)

            for arrow in self.arrows:
                arrow.draw(self.nodes_ax)

            self.nodes_canvas.draw()

    def draw_causes_graph(self, votes, utilities, winning_vote, round_num):
        self.update_sc_nodes_graph(round_num, winning_vote)
        vote_dict = {str(i) : votes[i] for i in range(len(votes))}
        self.update_arrows(vote_dict)
