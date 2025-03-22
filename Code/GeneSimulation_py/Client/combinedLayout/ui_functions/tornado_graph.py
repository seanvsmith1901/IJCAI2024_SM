import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from combinedLayout.colors import COLORS


def create_tornado_graph(main_window, fig, ax, y):
    ax.barh(y, [0 for _ in range(main_window.round_state.num_players)], color='red', label='Decrease Impact')
    ax.barh(y, [0 for _ in range(main_window.round_state.num_players)], color='green', label='Increase Impact')

    fig.patch.set_facecolor("#282828ff")
    ax.set_facecolor("#282828ff")
    ax.tick_params(color="#EBEBEB")
    ax.tick_params(color="#EBEBEB")
    ax.xaxis.set_tick_params(labelcolor="white")  # Set x-axis tick labels to white
    ax.yaxis.set_tick_params(labelcolor="white")  # (Optional) Set y-axis tick labels to white
    for spine in ax.spines.values():
        spine.set_color("#EBEBEB")

    return FigureCanvas(fig)

def update_tornado_graph(main_window, ax, positive_vote_effects, negative_vote_effects):
    ax.cla()  # Clear the axes

    num_players = main_window.round_state.num_players
    y_positions = np.arange(num_players)[::-1]  # Reverse order so Player 1 is on top

    # Initialize stacking positions
    left_neg = np.zeros(num_players)  # For negative impacts
    left_pos = np.zeros(num_players)  # For positive impacts

    max_extent = 0  # To determine symmetric x-axis limits

    for i in range(num_players):
        # player_index = num_players - 1 - i  # Reverse player order
        positive_votes = [positive_vote_effects[j][i] for j in range(num_players)]
        negative_votes = [negative_vote_effects[j][i] for j in range(num_players)]

        # Plot negative votes (extending left from zero)
        for j, negative_vote in enumerate(negative_votes):
            if negative_vote != 0:
                ax.barh(y_positions[i], negative_vote, left=left_neg[i], color=COLORS[j])
                left_neg[i] += negative_vote  # Update stacking position

        # Plot positive votes (extending right from zero)
        for j, positive_vote in enumerate(positive_votes):
            if positive_vote != 0:
                ax.barh(y_positions[i], positive_vote, left=left_pos[i], color=COLORS[j])
                left_pos[i] += positive_vote  # Update stacking position

        # Update max extent for symmetric x-axis
        max_extent = max(max_extent, abs(left_neg[i]), abs(left_pos[i]))

    # Set symmetric x-axis limits
    ax.set_xlim(-max_extent, max_extent)

    # Set labels and title
    ax.set_yticklabels([])
    for i, y_pos in enumerate(y_positions):
        ax.text(-max_extent * 1.05, y_pos, f"Player {i + 1}",
                             va='center', ha='right', fontsize=10, color=COLORS[i])

    ax.axvline(0, color='#EBEBEB', linewidth=2, linestyle='-')
    ax.figure.canvas.draw_idle()  # Redraw the figure