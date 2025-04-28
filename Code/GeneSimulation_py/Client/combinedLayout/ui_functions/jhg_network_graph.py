import numpy as np
from .StudyScripts.network import NodeNetwork
from ..colors import COLORS
import pyqtgraph as pg

def update_jhg_network_graph(main_window):
    if main_window.round_state.jhg_round_num == 0:
        current_popularity = np.full((main_window.round_state.num_players, main_window.round_state.num_players), 100)
    else:
        current_popularity = np.array(main_window.round_state.current_popularities)

    # Create the node network and initialize with current popularity
    net = NodeNetwork()
    net.setupPlayers([f"{i}" for i in range(np.shape(current_popularity)[0])])
    net.initNodes(init_pops=current_popularity)
    net.update(main_window.round_state.influence_mat, current_popularity) # Update the network with the influence matrix and current popularity

    # Set up the graph in the PyQtGraph widget
    main_window.jhg_network.clear()  # Clear any existing items
    node_positions = np.array([node.position[-1] for node in net.nodes])  # Create a scatter plot for the nodes

    spots = []
    for i, (x, y) in enumerate(node_positions):
        color = COLORS[i % len(COLORS)]  # Cycle through COLORS if there are more nodes than COLORS
        spots.append({'pos': (x, y), 'size': 15, 'brush': pg.mkBrush(color), 'pen': None})

    scatter = pg.ScatterPlotItem()
    scatter.addPoints(spots)  # Add all nodes with individual COLORS
    main_window.jhg_network.addItem(scatter)

    # Normalize the influence weights for color mapping and opacity
    min_weight = np.min(np.abs(main_window.round_state.influence_mat))
    max_weight = np.max(np.abs(main_window.round_state.influence_mat))

    def get_edge_color_and_opacity(weight):
        """Map influence weight to color and opacity."""
        # Normalize the weight to a 0-1 range
        normalized = (weight - min_weight) / (max_weight - min_weight) if max_weight != min_weight else 0

        # Green for positive, Red for negative
        if weight > 0:
            color = (0, 255, 0)  # Green for positive
        else:
            color = (255, 0, 0)  # Red for negative

        # Opacity scales with connection strength (stronger = more opaque)
        opacity = int(abs(255 * normalized))  # Full opacity (255) for strong connections, 0 for weak/no connection

        return color, opacity

    # Create edges based on the influence matrix
    for i, node in enumerate(net.nodes):
        for j, weight in enumerate(main_window.round_state.influence_mat[i]):
            if weight != 0:
                edge_color, opacity = get_edge_color_and_opacity(weight)
                pen = pg.mkPen(color=edge_color + (opacity,), width=2)

                # Create edge (PlotDataItem)
                line = pg.PlotDataItem([node_positions[i, 0], node_positions[j, 0]],
                                       [node_positions[i, 1], node_positions[j, 1]],
                                       pen=pen)  # Apply color and opacity

                line.setZValue(-1)  # Ensure edges are below the nodes
                main_window.jhg_network.addItem(line)

    main_window.jhg_network.scene().update()