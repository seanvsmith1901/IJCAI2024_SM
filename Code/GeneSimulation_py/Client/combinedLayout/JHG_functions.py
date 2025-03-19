import numpy as np
import pyqtgraph as pg

from StudyScripts.network import NodeNetwork

COLORS = ["#FF9191", "#D15C5E", "#965875", "#FFF49F", "#B1907D", "#FFAFD8", "#C9ADE9", "#fdbf6f"]

def update_jhg_ui_elements(main_window):
    for i in range(main_window.round_state.num_players):
        # If players[i] is the client, show tokens kept. Else, show the received and sent tokens for that player
        if i == int(main_window.round_state.client_id):
            main_window.round_state.players[i].kept_number_label.setText(str(int(main_window.round_state.received[i])))
        else:
            main_window.round_state.players[i].received_label.setText(str(int(main_window.round_state.received[i])))
            main_window.round_state.players[i].sent_label.setText(str(int(main_window.round_state.sent[i])))

        main_window.round_state.allocations[i] = 0
        main_window.round_state.players[i].popularity_label.setText(str(round(main_window.round_state.message["POPULARITY"][i])))
        main_window.round_state.players[i].popularity_over_time.append(main_window.round_state.message["POPULARITY"][i])
        main_window.round_state.players[i].allocation_box.setText("0")
        pen = pg.mkPen(COLORS[i])
        main_window.jhg_plot.plot(main_window.round_state.players[i].popularity_over_time, pen=pen)
        
def create_jhg_network_graph(main_window):
    if main_window.round_state.round_number == 0:
        current_popularity = np.full((main_window.round_state.num_players, main_window.round_state.num_players), 100)
    else:
        current_popularity = np.array(main_window.round_state.current_popularities)

    # Create the node network and initialize with current popularity
    net = NodeNetwork()
    net.setupPlayers([f"{i}" for i in range(np.shape(current_popularity)[0])])
    net.initNodes(init_pops=current_popularity)

    # Update the network with the influence matrix and current popularity
    net.update(main_window.round_state.influence_mat, current_popularity)

    # Set up the graph in the PyQtGraph widget
    main_window.jhg_network.clear()  # Clear any existing items

    # Create a scatter plot for the nodes
    node_positions = np.array([node.position[0] for node in net.nodes])  # Assuming node.position is a (x, y) tuple

    spots = []
    for i, (x, y) in enumerate(node_positions):
        color = COLORS[i % len(COLORS)]  # Cycle through COLORS if there are more nodes than COLORS
        spots.append({'pos': (x, y), 'size': 10, 'brush': pg.mkBrush(color), 'pen': None})

    scatter = pg.ScatterPlotItem()
    scatter.addPoints(spots)  # Add all nodes with individual COLORS
    main_window.jhg_network.addItem(scatter)

    # Normalize the influence weights for color mapping and opacity
    min_weight = np.min(main_window.round_state.influence_mat)
    max_weight = np.max(main_window.round_state.influence_mat)

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
        opacity = int(255 * normalized)  # Full opacity (255) for strong connections, 0 for weak/no connection

        return color, opacity

    # Now, create edges based on the influence matrix
    for i, node in enumerate(net.nodes):
        for j, weight in enumerate(main_window.round_state.influence_mat[i]):
            if weight != 0:
                edge_color, opacity = get_edge_color_and_opacity(weight)

                # Explicitly create the pen with the color and alpha
                pen = pg.mkPen(color=edge_color + (opacity,), width=2)  # Use a 4-tuple for (r, g, b, alpha)

                # Create edge (PlotDataItem)
                line = pg.PlotDataItem([node_positions[i, 0], node_positions[j, 0]],
                                       [node_positions[i, 1], node_positions[j, 1]],
                                       pen=pen)  # Apply color and opacity

                line.setZValue(-1)  # Ensure edges are below the nodes
                main_window.jhg_network.addItem(line)

    main_window.jhg_network.scene().update()  # Force refresh

def disable_jhg_buttons(main_window):
    for button in main_window.jhg_buttons:
        button.setEnabled(False)

def enable_jhg_buttons(main_window):
    for button in main_window.jhg_buttons:
        button.setEnabled(True)