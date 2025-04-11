from combinedLayout.colors import COLORS

def create_sc_nodes_graph(main_window):
    main_window.nodes_type = []
    main_window.nodes_text = []

    # Set background colors
    main_window.nodes_fig.patch.set_facecolor("#282828ff")
    main_window.nodes_ax.set_facecolor("#282828ff")

    # Hide ticks and tick labels
    main_window.nodes_ax.set_xticks([])
    main_window.nodes_ax.set_yticks([])
    main_window.nodes_ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    # Hide spines by setting their color to match background
    for spine in main_window.nodes_ax.spines.values():
        spine.set_color("#282828")

    # Turn off the grid and clear any pre-existing content
    main_window.nodes_ax.grid(False)
    main_window.nodes_ax.cla()

    return main_window.nodes_canvas


def update_sc_nodes_graph(main_window, winning_vote=None):
    # Clear axes before plotting
    main_window.nodes_ax.cla()

    radius = 5  # I just happen to know this, no clue if we need to make this adjustable based on server input.

    if winning_vote != None:
        if winning_vote == -1:
            print("NO ONE WON! NO RED.")
        else:
            print("WE HAVE A WINNING VOTE! ITS ", winning_vote)
            winning_vote += 1
    else:
        main_window.arrows.clear()

    # Instead of clearing the axes, let's just update the elements
    for arrow in main_window.arrows:
        arrow.draw(main_window.nodes_ax)  # Redraw the arrows if there are any. If there is a winning vote, we erase them.

    main_window.nodes_x = []
    main_window.nodes_y = []
    main_window.nodes_type = []
    main_window.nodes_text = []

    # Update node data
    for node in main_window.round_state.nodes:
        mini_dict = {"x_pos": float(node["x_pos"]), "y_pos": float(node["y_pos"])}
        main_window.nodes_dict[node["text"]] = mini_dict
        main_window.nodes_x.append(float(node["x_pos"]))
        main_window.nodes_y.append(float(node["y_pos"]))
        main_window.nodes_type.append(node["type"])
        main_window.nodes_text.append(node["text"])

    colors = []

    # Update or add annotations to the axes
    for i, (x_val, y_val) in enumerate(zip(main_window.nodes_x, main_window.nodes_y)):
        text = main_window.nodes_text[i]
        if text.startswith("Player"):
            split_string = text.split()
            text = split_string[1]
            color = COLORS[int(split_string[1]) - 1]
        elif text == "Cause " + str(winning_vote):
            color = "#e41e1e"  # red
        else:
            color = "#EBEBEB"

        # If an annotation already exists, update it; otherwise, create a new one
        annotations = [ann for ann in main_window.nodes_ax.texts if ann.get_text() == text]
        if annotations:
            # Update existing annotation
            annotations[0].set_position((x_val, y_val))
            annotations[0].set_color(color)
        else:
            # Create new annotation
            main_window.nodes_ax.annotate(
                text,
                (x_val, y_val),
                textcoords="offset points",
                xytext=(0, 3),
                ha='center',
                fontsize=9,
                color=color,
                weight='bold',
            )

        colors.append(color)

    main_window.nodes_ax.scatter(main_window.nodes_x, main_window.nodes_y, marker='o', c=colors)

    main_window.nodes_ax.set_aspect('equal', adjustable='box')

    main_window.nodes_canvas.draw()