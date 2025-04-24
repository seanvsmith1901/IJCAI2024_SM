from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from combinedLayout.colors import COLORS

from combinedLayout.Arrow import Arrow


class SCCausesGraph(QWidget):
    def __init__(self, num_cycles):
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
        self.num_cycles = num_cycles

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

            # Show round number
            self.nodes_ax.text(
                1.2, 1.1,  # top-right corner in axes coords
                f"Round {round_num}",
                transform=self.nodes_ax.transAxes,
                ha='right',
                va='top',
                fontsize=10,
                color='white',  # adjust for contrast; white looks good on dark bg
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#444444', edgecolor='none')
            )

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

            # Lists to store node info based on type
            player_x, player_y, player_colors, player_texts, player_text_colors = [], [], [], [], []
            cause_x, cause_y, cause_colors, cause_texts, cause_text_colors = [], [], [], [], []

            for i, (x_val, y_val) in enumerate(zip(self.nodes_x, self.nodes_y)):
                full_text = self.nodes_text[i]
                display_text = full_text
                text_color = 'black'  # default

                if full_text.startswith("Player"):
                    player_num = int(full_text.split()[1])
                    display_text = str(player_num)
                    color = COLORS[player_num - 1]

                    player_x.append(x_val)
                    player_y.append(y_val)
                    player_colors.append(color)
                    player_texts.append(display_text)
                    player_text_colors.append(text_color)

                elif full_text.startswith("Cause "):
                    display_text = full_text.replace("Cause ", "")
                    if winning_vote and full_text == f"Cause {winning_vote}":
                        color = "#e41e1e"  # red for winning cause
                        text_color = '#FFFFE0'
                    else:
                        color = "#EBEBEB"
                        text_color = '#1E3A5F'  # dark blue

                    cause_x.append(x_val)
                    cause_y.append(y_val)
                    cause_colors.append(color)
                    cause_texts.append(display_text)
                    cause_text_colors.append(text_color)

            # Draw annotations
            for x, y, text, color in zip(player_x, player_y, player_texts, player_text_colors):
                self.nodes_ax.annotate(text, (x - 0.05, y - 0.1), ha='center', va='center',
                                       fontsize=10, color=color, weight='bold', zorder=587)
            for x, y, text, color in zip(cause_x, cause_y, cause_texts, cause_text_colors):
                self.nodes_ax.annotate(text, (x, y - 0.25), ha='center', va='center',
                                       fontsize=10, color=color, weight='bold', zorder=587)

            # Draw nodes: players as circles, causes as triangles
            self.nodes_ax.scatter(player_x, player_y, marker='o', c=player_colors, s=150, zorder=500)
            self.nodes_ax.scatter(cause_x, cause_y, marker='^', c=cause_colors, s=180, zorder=501)

            self.nodes_ax.scatter(self.nodes_x, self.nodes_y, marker='o', c=colors, s=150)

            max_x = max(abs(x) for x in self.nodes_x)
            max_y = max(abs(y) for y in self.nodes_y)
            max_range = max(max_x, max_y) + 1  # Add some padding if you like

            self.nodes_ax.set_xlim(-max_range, max_range)
            self.nodes_ax.set_ylim(-max_range, max_range)

            self.nodes_ax.set_aspect('equal', adjustable='box')

            # Redraw the canvas
            self.nodes_canvas.draw()


    def update_arrows(self, votes, current_round_tab = False):
        # checks for existing arrows, and removes them.
        if votes:  # only run this if there are actual potential votes.
            for arrow in self.arrows:  # if there is anything in there.
                arrow.remove()

            self.arrows = []  # clean the arrows array.
            for key in votes:
                vote = votes[key] + 1
                if vote > 0:
                    player_name = "Player " + str(int(key) + 1)
                    start_x = self.nodes_dict[player_name]["x_pos"]
                    start_y = self.nodes_dict[player_name]["y_pos"]
                    cause_name = "Cause " + str(vote)
                    end_x = self.nodes_dict[cause_name]["x_pos"]
                    end_y = self.nodes_dict[cause_name]["y_pos"]

                    new_arrow = Arrow((start_x, start_y), (end_x, end_y), color=COLORS[int(key)])
                    self.arrows.append(new_arrow)

            for arrow in self.arrows:
                arrow.draw(self.nodes_ax)

        if self.round_state.sc_cycle and current_round_tab:
            self.update_cycle_label(self.round_state.sc_cycle, current_round_tab)
        elif votes:
            self.nodes_canvas.draw()

    def draw_causes_graph(self, votes, utilities, winning_vote, round_num):
        self.update_sc_nodes_graph(round_num, winning_vote)
        self.update_arrows(votes)

    def update_cycle_label(self, cycle, current_round_tab = False):
        if cycle and cycle <= self.num_cycles and current_round_tab:
            self.nodes_ax.text(
                1.2, 1,  # top-right corner in axes coords
                f"Cycle {cycle}/{self.num_cycles} ",
                transform=self.nodes_ax.transAxes,
                ha='right',
                va='top',
                fontsize=10,
                color='white',  # adjust for contrast; white looks good on dark bg
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#444444', edgecolor='none')
            )
        self.nodes_canvas.draw()