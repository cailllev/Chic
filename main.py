from itertools import combinations_with_replacement, product
import matplotlib.pyplot as plt
from pprint import pprint

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
            curr_combinations = get_all_throws(dice_count)  # all combinations with given dice count
            cleaned = sort_out_1s_and_6s(curr_combinations)
            add_dice_stats(next_dice_stats, cleaned, comb_counts)
        dice_stats = next_dice_stats.copy()
        print(f"[#]   Count of all possible Combinations: {sum(dice_stats)}")
        print(f"[#]   Dice Stats >> {', '.join([str(i) +':' + str(d) for i, d in enumerate(dice_stats)])}")
    return dice_stats


def re_add_ones(throws, dice_count):
    """
    [[2, 3], [4], [6, 6]] -> [[1, 2, 3], [1, 1, 4], [1, 6, 6]]
    """
    for t in throws:
        t.extend([1] * (dice_count - len(t)))


def get_final_combinations(dice_stats: list) -> dict:
    # combinations_with_replacement('ABCD', 2) -> AA AB AC AD BB BC BD CC CD DD
    possible_throws = combinations_with_replacement(dice_vals, dice)
    count_combinations = {t: 0 for t in possible_throws}

    for dice_count, comb_counts in enumerate(dice_stats):
        curr_combinations = get_all_throws(dice_count)
        re_add_ones(curr_combinations, dice)
        for c in curr_combinations:
            c.sort()  # [5, 1, 2] -> [1, 2, 5] the same throw
            count_combinations[tuple(c)] += comb_counts
    return count_combinations


def show_chart(counts):
    x = [str(k) for k in counts.keys()]
    y = [str(v) for v in counts.values()]
    # y = [str(round(v * 100, 1)) + "%" for v in counts.values()]
    plt.bar(x, y)
    plt.title("Throws Distribution")
    plt.xlabel("Throw")
    plt.ylabel("Throw reached X times")
    plt.show()


def calc_score(combinations):
    sums = {}
    for comb, count in combinations.items():
        sum1 = sum(comb)
        sum2 = sum([d if d != 1 else 100 for d in comb])  # count 1s as 100s
        sums[comb] = count, (sum1, sum2)
    return sums


def compare_combinations(combinations):
    # count by how many other combinations a given combination can be beaten
    ranks = {}
    for comb, (count, (as_1, as_100)) in combinations.items():
        # can count 1s as 1s oder 100s -> 2,2,2 is the lowest when 1s as 100s, 6,6,6 is highest when 1s as 1s
        lower_when_1_count = 0
        lower_when_100_count = 0
        higher_when_1_count = 0
        higher_when_100_count = 0
        for other_comb, (other_count, (other_as_1, other_as_100)) in combinations.items():
            if comb == other_comb:
                continue
            if other_as_1 < as_1:
                lower_when_1_count += count
            if other_as_100 < as_100:
                lower_when_100_count += count
            if other_as_1 > as_1:
                higher_when_1_count += count
            if other_as_100 > as_100:
                higher_when_100_count += count
        ranks[comb] = lower_when_1_count, lower_when_100_count, higher_when_1_count, higher_when_100_count
    return ranks


def get_choices(combinations, strats, sum_of_combinations):
    choices = {}
    for comb, beaten_counts in combinations.items():
        s = "Chance of losing, winning: "
        c = min(beaten_counts)
        i = beaten_counts.index(c)
        losing_ratio = c / sum_of_combinations
        for player_count in range(2, 6):  # calc chances for 2 to 6 players
            # losing in 4 player game = none is worse -> 10% lost vs avg. -> 0.1 ** 3
            # winning in 4 player game = none is better -> 90% win vs avg. -> 0.9 ** 3
            chance_to_lose = str(round(losing_ratio ** (player_count - 1), 4))
            chance_to_win = str(round((1-losing_ratio) ** (player_count - 1), 4))
            s += chance_to_lose + ", " + chance_to_win + " / "
        s = s[:-3]
        choices[comb] = strats[i], s
    return choices


def main():
    # get dice left before last throw
    stats = get_dice_stats(rounds)

    # get all possible combinations and count it, e.g. > (2, 4, 6): 75264
    combinations = get_final_combinations(stats)
    sum_of_combinations = sum([count for count in combinations.values()])
    print("[*] Round 3")
    print("[#]   Count of all possible Combinations:", sum_of_combinations)
    print("\n[*] Combinations:")
    pprint(combinations)

    combinations_with_scores = calc_score(combinations)
    print("\n[*] Combinations with Scores:")
    pprint(combinations_with_scores)

    combinations_compared = compare_combinations(combinations_with_scores)
    print("\n[*] Combinations Compared:")
    pprint(combinations_compared)

    strats = ["1s as   1s and lower ", "1s as 100s and lower ",
              "1s as   1s and higher", "1s as 100s and higher"]
    choice_per_combination = get_choices(combinations_compared, strats, sum_of_combinations)
    print("\n[*] Combinations Strategy:")
    for elem in choice_per_combination.items():
        print(elem)


if __name__ == "__main__":
    main()
