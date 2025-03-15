import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from PIL import Image, ImageOps

from network import NodeNetwork
from engine import JHGEngine


player2color = {
    'Govt': '#e7298a',
    'CAT': '#fc8d62',
    'Gene': '#8da0cb',
    'Human': '#34bdc5'
}

def load_data(game_code, folder):
    df = pd.read_csv(f'./{folder}/csvs/jhg_{game_code}.csv')
    plrs = len([c for c in df.columns if c[:3] == 'pid'])
    pop_cols = [f'p{i}' for i in range(plrs)]
    pid_cols = [f'pid{i}' for i in range(plrs)]
    action_cols = [f'{i}-T-{j}' for i in range(plrs) for j in range(plrs)]
    infl_cols = [f'{i}-I-{j}' for i in range(plrs) for j in range(plrs)]
    pop_mat = df[pop_cols].to_numpy()
    pids = {i: t for i, t in enumerate(df[pid_cols].to_numpy()[0])}
    actions_mat = df[action_cols].to_numpy().reshape(-1, plrs, plrs)
    infl_mat = df[infl_cols].to_numpy().reshape(-1, plrs, plrs)
    params = {
        'alpha': df['alpha'][0],
        'beta': df['beta'][0],
        'give': df['give'][0],
        'keep': df['keep'][0],
        'steal': df['steal'][0],
        'num_players': plrs
    }

    return pids, pop_mat, actions_mat, infl_mat, params

def plot_game(game_code, rounds, folder):
    pids, pop_mat, actions_mat, infl_mat, params = load_data(game_code, folder)
    print(pop_mat.shape, actions_mat.shape, infl_mat.shape)

    dpi = 200
    fig = plt.figure(figsize=(10, 5), dpi=dpi)

    names = [f'p{k}' for k, v in pids.items()]
    player_types = {f'p{k}': v for k, v in pids.items()}
    #letters = 'ABCDEFGH'
    letters = '01234567'
    name2codename = {} #{n: letters[i] for i, n in enumerate(names)}
    if len(set([v for k, v in pids.items()])) > 1:
        #name2color = {f'p{k}': '#34bdc5' if v == 'Human' else '#f47c6f' for k, v in pids.items()}
        name2color = {f'p{k}': player2color.get(v, '#f47c6f') for k, v in pids.items()}
        legend_colors = {v if v != "Bot" else "CAB": player2color.get(v, '#f47c6f') for k, v in pids.items()}
    else:
        name2color = None
        legend_colors = None

    net = NodeNetwork()
    net.setupPlayers(names, player_types)
    net.initNodes(init_pops=pop_mat[0])

    print(params)
    engine = JHGEngine(**params)

    gs = GridSpec(2, len(rounds), figure=fig)
    ids = [(1, i)for i in range(len(rounds))]
    for r in range(pop_mat.shape[0]):
        net.update(infl_mat[r], pop_mat[r])
        if r in rounds:
            round_idx = rounds.index(r)
            ax = fig.add_subplot(gs[ids[round_idx][0], ids[round_idx][1]], facecolor='c' if r%2 ==1 else 'm', ymargin=-.4)
            net.graphExchange(ax, fig, actions_mat[r], color_lookup=name2color, name_lookup=name2codename)
            ax.set_title(f'Round {r}', fontsize=12, loc='center', y=-0.09)
    ax = fig.add_subplot(gs[0, :])
    net._graphPopularities(ax, fig, pop_mat, color_lookup=name2color, name_lookup=name2codename, legend_colors=legend_colors)
    fig.subplots_adjust(wspace=0.0, hspace=0.06)

    #plt.show()
    image_path = f'./images/storyplot_{game_code}.png'
    plt.savefig(image_path)

    image = Image.open(image_path)

    gray_image = ImageOps.grayscale(image)

    threshold_value = 254  # Adjust this value as needed
    thresholded_image = gray_image.point(lambda p: p < threshold_value and 255)
    #thresholded_image.show()
    bbox = thresholded_image.getbbox()

    cropped_image = image.crop(bbox)

    cropped_image.save(image_path)
    cropped_image.show()


def plot_network(game_code, folder, rounds=None):
    pids, pop_mat, actions_mat, infl_mat, params = load_data(game_code, folder)
    print(pop_mat.shape, actions_mat.shape, infl_mat.shape)

    dpi = 200
    if rounds is None:
        rounds = [i for i in range(pop_mat.shape[0])]
    fig = plt.figure(figsize=(2*len(rounds), 5), dpi=dpi)

    names = [f'p{k}' for k, v in pids.items()]
    player_types = {f'p{k}': v for k, v in pids.items()}
    #letters = 'ABCDEFGH'
    #name2codename = {n: letters[i] for i, n in enumerate(names)}
    name2codename = {}
    if len(set([v for k, v in pids.items()])) > 1:
        #name2color = {f'p{k}': '#34bdc5' if v == 'Human' else '#f47c6f' for k, v in pids.items()}
        name2color = {f'p{k}': player2color.get(v, '#f47c6f') for k, v in pids.items()}
        legend_colors = {v: player2color.get(v, '#f47c6f') for k, v in pids.items()}
    else:
        name2color = None
        legend_colors = None

    net = NodeNetwork()
    net.setupPlayers(names, player_types)
    net.initNodes(init_pops=pop_mat[0])

    gs = GridSpec(1, len(rounds), figure=fig)
    ids = [(0, i)for i in range(len(rounds))]
    for r in range(pop_mat.shape[0]):
        net.update(infl_mat[r], pop_mat[r])
        if r in rounds:
            round_idx = rounds.index(r)
            ax = fig.add_subplot(gs[ids[round_idx][0], ids[round_idx][1]], facecolor='c' if r%2 ==1 else 'm', ymargin=-.4)
            net.graphExchange(ax, fig, actions_mat[r], color_lookup=name2color, name_lookup=name2codename)
            ax.set_title(f'Round {r}', fontsize=12, loc='center', y=-0.09)
    fig.subplots_adjust(wspace=0.0, hspace=0.00)

    #plt.show()
    image_path = f'./images/networkplot_{game_code}.png'
    plt.savefig(image_path)

    image = Image.open(image_path)

    gray_image = ImageOps.grayscale(image)

    threshold_value = 254  # Adjust this value as needed
    thresholded_image = gray_image.point(lambda p: p < threshold_value and 255)

    bbox = thresholded_image.getbbox()

    cropped_image = image.crop(bbox)

    cropped_image.save(image_path)
    cropped_image.show()



if __name__ == "__main__":
    """
    Bot Game: VBLN

    Human game: QLHS
        p0: Bravo/Ethan
        p1: Charlie/Tim
        p2: Echo/Galahad
        p3: Foxtrot/John Doe
        p4: Oscar/Crandallberry
        p5: Papa/Birthday Girl
        p6: X-ray/lab rat #001

    """
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-c", "--game_code",
        type=str,
        required=True,
        help="game code to load"
    )
    
    parser.add_argument(
        "-r", "--rounds",
        type=int,
        nargs="+",
        help="list of rounds to plot"
    )

    parser.add_argument("-f", "--folder", type=str,
        choices=["study_games", "other_games", "sim_games"],
        default="study_games", 
        help="which is the folder to load games from")

    parser.add_argument("-p", "--plot_type", type=str,
        choices=["story", "network"],
        default="story", 
        help="which type of plot to create")
    
    args = parser.parse_args()

    if args.plot_type == 'story':
        plot_game(args.game_code, args.rounds, args.folder)
    elif args.plot_type == 'network':
        plot_network(args.game_code, args.folder, args.rounds)
