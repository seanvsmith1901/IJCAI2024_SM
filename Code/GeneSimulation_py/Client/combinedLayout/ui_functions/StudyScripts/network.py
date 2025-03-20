import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from time import time
import logging

# from graphutils import colors, find_endpts

"""

            e1, e2, e3, e4 = find_endpts(
                np.array([[x[i]], [y[i]]]),
                np.array([[x[j]], [y[j]]]),
                theta=np.pi / 18,
                radius=0.2)

            pp1 = mpatches.FancyArrowPatch(
                (e2[0, 0], e2[1, 0]), (e3[0, 0], e3[1, 0]), 
                color=line_color, 
                connectionstyle="arc3,rad=0.1",
                arrowstyle="Simple,head_width=5,head_length=10")

            ax.add_patch(pp1)

"""


def generateIdealMatrix(relation_mat):
    ideal_mat = deepcopy(relation_mat)
    ideal_mat[ideal_mat == 1.0] = 0.0
    np.fill_diagonal(ideal_mat, 0.0)

    sign_mat = np.sign(ideal_mat)

    for i in range(0, len(sign_mat)):
        for j in range(i, len(sign_mat)):
            sign_mat[i, j] = sign_mat[j, i] = -1 if sign_mat[i, j] == -1 or  sign_mat[j, i] == -1 else 1 if sign_mat[i, j] == 1 or  sign_mat[j, i] == 1 else 0

    ideal_mat = np.abs(ideal_mat)
    ideal_mat = (ideal_mat + ideal_mat.T) / 2.0
    ideal_mat = ideal_mat * sign_mat
    ideal_mat[ideal_mat != 0] += np.amax(ideal_mat) - np.amin(ideal_mat)
    ideal_mat[ideal_mat != 0] = np.round(np.amax(ideal_mat) / ideal_mat[ideal_mat != 0], decimals=2)
    #ideal_mat[ideal_mat == 0] += np.mean(ideal_mat[ideal_mat != 0])
    np.fill_diagonal(ideal_mat, 0.0)

    return ideal_mat

class Node:
    '''
    Rules for potential fields:

    01) postive attraction is proportional to distance
    02) negative repulsion is inverse proportional to distance
    03) negative repulsion keeps all nodes from colliding
    04) universal jitter occurs at all steps
    05) nodes drop in order of popularity
    06) there is a universe total distance requirement that scales with the number of nodes
    07) nodes drop at random point or centroid (?)
    08) nodes update in reverse order of popularity
    09) positive attraction is when you receive from someone (?)
    10) negative repulsion is when you take from one one (?)
    '''
    def __init__(self, init_pos, name, code, popularity):
        self.init_pos = init_pos
        self.position = []
        self.position.append(np.array(self.init_pos))
        self.code = code
        self.popularity = popularity
        self.min_margin =  5 #1.25
        self.name = name
        self.init_lr = 0.01
        self.lr = self.init_lr
        self.previous_step = None
        self.max_step = 1.0
        self.type = 'agent' #TODO: Change this so that it is read in and can be changed between agent and institution

    def reset(self):
        self.lr = self.init_lr
        self.position = []
        self.position.append(np.array(self.init_pos))

    def setPopularity(self, popularity):
        self.popularity = popularity

    def getSize(self):
        return self.popularity

    def getCurrentPos(self):
        return self.position[-1]

    def update(self, others, relation_mat):
        '''
        x1, x2, y1, y2 = sp.symbols('x1 x2 y1 y2')
        dist = ( (x1 - y1)**2 + (x2 - y2)**2 )**(1/2)
        d_xy = sp.Symbol('d_xy')
        error = (d_xy - dist)**2
        '''
        dist = lambda x, y: ( (x[0] - y[0])**2 + (x[1] - y[1])**2 )**(1/2)

        self_pos = self.getCurrentPos()

        pos_dot = np.zeros_like(self_pos)

        ideal_mat = generateIdealMatrix(relation_mat)

        for other in others:
            other_pos = other.getCurrentPos()
            if self.code != other.code and (ideal_mat[self.code, other.code] != 0.0 or ideal_mat[other.code, self.code] != 0.0 or self.min_margin > dist(self_pos, other_pos)):
                ideal_dist = ideal_mat[self.code, other.code]
                if ideal_dist < 1.0:
                    ideal_dist = self.min_margin

                x1_error = -2*(ideal_dist - ((self_pos[0] - other_pos[0])**2 + (self_pos[1] - other_pos[1])**2)**0.5)*(1.0*self_pos[0] - 1.0*other_pos[0])*((self_pos[0] - other_pos[0])**2 + (self_pos[1] - other_pos[1])**2)**(-0.5)
                x2_error = -2*(ideal_dist - ((self_pos[0] - other_pos[0])**2 + (self_pos[1] - other_pos[1])**2)**0.5)*(1.0*self_pos[1] - 1.0*other_pos[1])*((self_pos[0] - other_pos[0])**2 + (self_pos[1] - other_pos[1])**2)**(-0.5)

                pos_dot += np.array([x1_error, x2_error]).astype(float)

        self.position.append(self.position[-1] - self.lr * pos_dot)

class NodeNetwork:

    def __init__(self):
        self.steps = 50
        self.setEmpty()
        self.color_scheme_id = 'colorScheme2'

    def setEmpty(self):
        self.players = []
        self.players2code = {}
        self.code2players = {}
        self.nodes = []
        self.init_pos = {}

    def reset(self):
        self.altered_popularities = {}

    def setupPlayers(self, player_names, player_types={}):
        self.players = player_names
        self.player_types = player_types

        theta = 2*np.pi / len(self.players)
        r = 1.0

        for i, player in enumerate(self.players):
            self.players2code[player] = i
            self.code2players[i] = player
            self.init_pos[i] = [r*np.cos(theta*i), r*np.sin(theta*i)]

    def initNodes(self, init_pops):
        # self.nodes.append([])
        for code_id in range(len(self.players)):
            next_node = Node(
                init_pos=self.init_pos[code_id],
                name=self.code2players[code_id],
                code=code_id,
                popularity=init_pops[code_id])
            self.nodes.append(next_node)

    def update(self, adj, pops):
        # self.nodes.append(deepcopy(self.nodes[-1]))
        for i in range(len(self.nodes)):
            self.nodes[i].popularity = pops[i]
        for _ in range(self.steps):
            for curr_node in self.nodes[::-1]:
                other_nodes = [node for node in self.nodes if node.code != curr_node.code]
                curr_node.update(other_nodes, adj)

    def backStep(self):
        self.nodes.pop()

    def _graphPopularities(self, ax, fig, pops_arr, color_lookup=None, name_lookup={}, legend_colors={}):
        rounds = len(pops_arr)
        final_rank = np.argsort(np.argsort(pops_arr[-1].flatten()))
        for n, node in enumerate(self.nodes[-1]):
            if color_lookup is None:
                i = self.players2code[node.name]
                color_idx = i % len(colors[self.color_scheme_id])
                player_color = colors[self.color_scheme_id][color_idx]
            else:
                player_color = color_lookup[node.name]
            marker = 'o' if self.player_types.get(node.name, 'Human') == 'Human' else 'D'

            if color_lookup is not None:
                node_label = f'{name_lookup.get(node.name, node.name)} ({self.player_types.get(node.name, "")})'
            else:
                node_label = f'{name_lookup.get(node.name, node.name)}'
            ax.plot(np.arange(rounds), pops_arr[:, n], color=player_color, label=node_label, marker=marker, linestyle='dashed')
            if final_rank[n] < 5:
                y_pos = (final_rank[n]/len(self.nodes[-1]) * 70 - 10)
            elif final_rank[n] != 7:
                y_pos = (final_rank[n]/len(self.nodes[-1]) * 35 - 10)
            else:
                y_pos = 0

            if color_lookup is not None:
                ax.annotate(name_lookup.get(node.name, node.name), (rounds-1, pops_arr[-1, n]), xytext=(30, y_pos), textcoords='offset points', arrowprops={'arrowstyle': '->'})

        ax.set_xticks(np.arange(rounds+1 if rounds >= 10 and rounds % 2 == 1 else rounds, step=1 if rounds < 10 else 2))

        #ax.set_ylim(-30, 550)
        ax.set_xlabel('Round', fontsize=12)
        ax.set_ylabel('Popularity', fontsize=12)

        if color_lookup is not None:
            if legend_colors is None:
                legend_elements = [
                    Line2D([0], [0], marker='o', color='w', label='Human',
                                markerfacecolor='#34bdc5', markersize=10),
                    Line2D([0], [0], marker='D', color='w', label='Bot',
                                markerfacecolor='#f47c6f', markersize=10)
                ]
            else:
                legend_elements = [
                    Line2D([0], [0], marker='D', color='w', label=label,
                                markerfacecolor=color, markersize=10)
                                for label, color in legend_colors.items()
                ]
            ax.legend(handles=legend_elements, loc='upper left')
        else:
            ax.legend(loc='upper left', ncol=2)
        #ax.grid(True)

    def graphExchange(self, ax, fig, exchanges, step=-1, color_lookup=None, name_lookup={}):
        max_x = float('-inf')
        min_x = float('inf')
        max_y = float('-inf')
        min_y = float('inf')
        max_size = 0

        circle_markers = []
        marker_names = []

        max_pop = 0

        for node in self.nodes[-1]:
            max_pop = max(max_pop, node.popularity)

        rad_divisor = 3.5
        min_rad = 0.2

        get_rad = lambda p: max(p/max_pop/rad_divisor, min_rad)

        for p_i in self.nodes[-1]:
            for p_j in self.nodes[-1]:
                i = p_i.code
                j = p_j.code
                if exchanges[i, j] != 0 and i != j:
                    pos_i = p_i.position[step]
                    pos_j = p_j.position[step]
                    line_color = '#d95f02' if exchanges[i, j] < 0 else '#1b9e77'

                    e1, e2, e3, e4 = find_endpts(
                        pos_i,
                        pos_j,
                        theta=np.pi / 9,
                        radius1=get_rad(p_i.popularity),
                        radius2=get_rad(p_j.popularity))

                    pp1 = mpatches.FancyArrowPatch(
                        (e2[0], e2[1]), (e3[0], e3[1]),
                        color=line_color,
                        #edgecolor= '#d95f0288' if exchanges[i, j] < 0 else '#1b9e7788',#'#00000008',
                        connectionstyle="arc3,rad=0.2",
                        arrowstyle=f"Simple,head_width=2,head_length=2,tail_width={0.2 + 0*abs(exchanges[i, j]) / len(self.nodes[-1])}")

                    ax.add_patch(pp1)

        for node in self.nodes[-1]:
            if color_lookup is None:
                player_idx = self.players2code[node.name]
                color_idx = player_idx % len(colors[self.color_scheme_id])
                player_color = colors[self.color_scheme_id][color_idx]
            else:
                player_color = color_lookup[node.name]
            circle_color = player_color
            """if self.player_types.get(node.name, 'Human') == 'Bot':
                circle_color = '#AAAAAAAA'"""
            radius = get_rad(node.popularity)
            circle = plt.Circle(
                (node.position[step][0], node.position[step][1]),
                radius,
                label="{} @{}".format(name_lookup.get(node.name, node.name), np.round(node.popularity)),
                edgecolor=circle_color,
                facecolor='#F0F0F088',
                fill=not np.isclose(node.popularity, 0) or True,
                alpha=0.75)
            ax.add_artist(circle)
            circle_markers.append(circle)

            if self.player_types.get(node.name, 'Human') == 'Bot' and False:
                # Remove the False to have it draw the bots with a diamond
                polygon = mpatches.RegularPolygon(
                    (node.position[step][0], node.position[step][1]),
                    4,
                    radius=radius * 0.8,
                    color=player_color if node.popularity > 0 or True else "#00000088",
                    fill=node.popularity > 0 or True
                )
                ax.add_artist(polygon)

            ax.annotate("{}".format(name_lookup.get(node.name, node.name)),
                (node.position[step][0], node.position[step][1]), xytext=(0, 0), textcoords='offset points', va="center", ha="center", fontsize=7, c='k', weight='bold')
            marker_names.append("{} @{}".format(name_lookup.get(node.name, node.name), np.round(node.popularity)))
            max_x = max(max_x, node.position[step][0])
            min_x = min(min_x, node.position[step][0])
            max_y = max(max_y, node.position[step][1])
            min_y = min(min_y, node.position[step][1])
            max_size = max(max_size, circle.radius)

        ax.set_xlim(xmin=min(min_x, min_y) - 2*max_size, xmax=max(max_x, max_y) + 2*max_size)
        ax.set_ylim(ymin=min(min_x, min_y) - 2*max_size, ymax=max(max_x, max_y) + 2*max_size)

        ax.set_axis_off()
        ax.set_aspect('equal')
        #ax.grid(True)
        #fig.subplots_adjust(top=1.0)

    def __str__(self):
        ret = f'{type(self).__name__}'
        for r, n in self.nodes.items():
            ret += f'\n\tRound {r}: {n}'
        return ret