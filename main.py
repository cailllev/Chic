from itertools import product

dice_vals = list(range(1, 7))
dice = 3
rounds = 3


def get_all_throws(dice_count) -> list[list]:
    return [list(c) for c in product(dice_vals, repeat=dice_count)]


def sort_out_1s_and_6s(throws: list[list]) -> list[list]:
    """
    converts two 6s to one 1, three 6s to two 1s, and removes all 1s
    :param throws: dice throws, like [[1, 6, 6], [2, 1, 3], ...]
    :return: [[6], [2, 3], ...]
    """
    sorted_out = []
    for throw in throws:
        if throw.count(6) == 3:  # 3x6s = 2x1s -> one dice left
            throw = [6]
        if throw.count(6) == 2:  # 2x6s = 1x1s -> 2 dice left
            throw = [d for d in throw if d != 6]  # keep other dice
            throw.append(6)  # append one 6 again
        throw = [d for d in throw if d != 1]  # remove 1s
        sorted_out.append(throw)
    return sorted_out


def add_dice_stats(existing_stats: list, cleaned_throws: list[list], combinations_per_throw: int):
    if combinations_per_throw == 0:
        return existing_stats
    for t in cleaned_throws:
        existing_stats[len(t)] += combinations_per_throw


def get_dice_stats(count_rounds: int) -> list:
    # track how many dice are left after each throw with each combination
    dice_stats = [0] * (dice+1)
    dice_stats[-1] = 1  # all X dice left, and one possibility leading to this (the start of a turn)

    for r in range(count_rounds - 1):
        print("[*] Round", r+1)
        next_dice_stats = [0] * (dice+1)
        for dice_count, comb_counts in enumerate(dice_stats):
            combinations = get_all_throws(dice_count)  # all combinations with given dice count
            cleaned = sort_out_1s_and_6s(combinations)
            add_dice_stats(next_dice_stats, cleaned, comb_counts)
        dice_stats = next_dice_stats.copy()
        print(f"[#]  Count of all possible Combinations: {sum(dice_stats)}")
        print(f"[#]  Dice Stats >> {', '.join([str(i) +':' + str(d) for i, d in enumerate(dice_stats)])}")
    return dice_stats


# get dice left before last throw
stats = get_dice_stats(rounds)

# TODO now calc possibilities of outcomes ([1, 1, 1], [1, 1, 2], ...) given the stats before last round
