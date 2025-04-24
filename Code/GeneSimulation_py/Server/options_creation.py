from random import randrange, shuffle, randint

even_two_plus_one = {
    5: [2, 2], 6: [0], 7: [3, 3], 8: [3, 3], 9: [4, 4], 10: [4, 4], 11: [4, 4], 12: [5, 5], 13: [5,5],
    14: [6, 6], 15: [6, 6], 16: [6, 6], 17: [7, 7], 18: [7, 7], 19: [7, 7], 20: [8, 8]
}

small_minority_two_plus_one = {
    5: [2, 2], 6: [3, 2], 7: [3, 3], 8: [3, 3], 9: [4, 4], 10: [4, 4], 11: [5, 4], 12: [5, 5], 13: [5, 5], 14: [6, 6],
    15: [6, 6], 16: [7, 6], 17: [7, 7], 18: [8, 7], 19: [8, 8], 20: [9, 9]
}

large_minority_two_plus_one = {
    5: [2, 2], 6: [3, 2], 7: [3, 3], 8: [3, 3], 9: [4, 3], 10: [4, 4], 11: [4, 4], 12: [5, 5], 13: [5, 5], 14: [6, 5],
    15: [6, 6], 16: [6, 6], 17: [7, 6], 18: [7, 6], 19: [7, 7], 20: [8, 7]
}

group_size_options = {
    0: even_two_plus_one,
    1: small_minority_two_plus_one,
    2: large_minority_two_plus_one
}


def generate_two_plus_one_groups(num_players, group_option):
    group_sizes = group_size_options[group_option]
    players = [i + 1 for i in range(num_players)]
    if num_players < 5:
        raise ValueError("Must have at least 5 players to generate a two plus one group")
    if group_sizes[num_players][0] == 0:
        raise ValueError(f"This group_size scheme is incompatible with {num_players} players")

    group1 = []
    group2 = []
    group1_size = group_sizes[num_players][0]
    group2_size = group_sizes[num_players][1]

    for _ in range(group1_size):
        group1.append(players.pop(randrange(0, len(players))))
    for _ in range(group2_size):
        group2.append(players.pop(randrange(0, len(players))))
    group3 = players

    return {1: group1, 2: group2, 3: group3}

def generate_two_plus_one_groups_options_best_of_three(groups):
    players = groups[1] + groups[2] + groups[3]

    group_order = [0, 1, 2]
    shuffle(group_order)
    group_cols = {0: group_order[0], 1: group_order[1], 2: group_order[2]}
    options = [[] for _ in range(len(players))]

    # Generate the utility scores for each player and assign it to the same column as everyone else in their group
    for i in range(len(groups)):
        group_col = group_cols[i]
        for player in groups[i + 1]:
            generated_options = [randint(-8, 8) for _ in range(3)]
            max_index = generated_options.index(max(generated_options))
            # Swap the highest value with the groups column
            generated_options[max_index], generated_options[group_col] = generated_options[group_col], generated_options[max_index]
            for i in range(len(generated_options)):
                generated_options[i] += randint(-2,2)
            options[player - 1] = generated_options

    return options