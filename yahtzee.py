from collections import Counter
import itertools

import numpy as np


# assume values are sorted in Roll
Roll = tuple[int, int, int, int, int]


def score_upper_section(roll: Roll, number: int) -> int:
    return sum(value for value in roll if value == number)


def score_kind(roll: Roll, min_count: int) -> int:
    if Counter(roll).most_common(1)[0][1] >= min_count:
        return sum(roll)
    return 0


def score_full_house(roll: Roll) -> int:
    min_value = roll[0]
    max_value = roll[-1]
    if min_value != max_value and roll in {
        (min_value, min_value, min_value, max_value, max_value),
        (min_value, min_value, max_value, max_value, max_value),
    }:
        return 25
    return 0


def score_small_straight(roll: Roll) -> int:
    roll = set(roll)
    if any(set(range(idx, idx + 4)) <= roll for idx in range(1, 4)):
        return 30
    return 0


def score_large_straight(roll: Roll) -> int:
    if roll in {(1, 2, 3, 4, 5), (2, 3, 4, 5, 6)}:
        return 40
    return 0


def score_yahtzee(roll: Roll) -> int:
    if roll[0] == roll[-1]:
        return 50
    return 0


def score_chance(roll: Roll) -> int:
    return sum(roll)


score_functions = {
    name: lambda roll: score_upper_section(roll, value)
    for value, name in enumerate(["ones", "twos", "threes", "fours", "fives", "sixes"], 1)
}
score_functions.update(
    {
        "three of a kind": lambda roll: score_kind(roll, 3),
        "four of a kind": lambda roll: score_kind(roll, 4),
        "full house": score_full_house,
        "small straight": score_small_straight,
        "large straight": score_large_straight,
        "yahtzee": score_yahtzee,
        "chance": score_chance,
    }
)


class YahtzeeOptimizer:

    def __init__(self, saved_values_file: str | None = None):
        self.possible_upper_section_scores = self.compute_possible_upper_section_scores()
        if saved_values_file is None:
            self.state_values = self.compute_state_values()
        else:
            self.state_values = self.load_state_values_from_file(saved_values_file)

    @classmethod
    def compute_possible_upper_section_scores(cls) -> dict[
        tuple[bool, bool, bool, bool, bool, bool], set[int] | tuple[int, int]
    ]:
        # For each possible bit vector of length 6, indicating which of the upper sections
        # are filled out, get the set of possible total scores for the upper section capped
        # at 63. Also, denote a range of possible scores with a tuple (min, max + 1).
        max_score = 63
        possible_scores = {
            (False,) * 6: (0, 1),
        }
        for num_filled in range(1, 6):
            for filled in itertools.combinations(range(1, 7), num_filled):
                prev_scores = possible_scores[cls._to_bit_vector(filled[1:], 1, 7)]
                if isinstance(prev_scores, tuple):
                    prev_scores = range(*prev_scores)
                scores = set().union(
                    *(
                        range(prev_score, prev_score + filled[0] * 6, filled[0])
                        if prev_score < max_score
                        else [max_score]
                        for prev_score in prev_scores
                    )
                )
                scores = {min(score, max_score) for score in scores}
                lo, hi = min(scores), max(scores)
                if len(scores) == hi - lo + 1:
                    scores = (lo, hi + 1)
                possible_scores[cls._to_bit_vector(filled, 1, 7)] = scores

        # Even though all scores from 0 to 63 are possible when all 6 upper sections are filled,
        # the value of the score doesn't matter in this case because you would have already received
        # the bonus, so we just set the possible scores to {0}.
        possible_scores[(True,) * 6] = (0, 1)

        return possible_scores

    @staticmethod
    def _to_bit_vector(inds: tuple[int, ...], lo: int, hi: int) -> tuple[bool, ...]:
        bit_vector = np.zeros(hi - lo, dtype=bool)
        bit_vector[np.array(inds, dtype=int) - lo] = True
        return tuple(bit_vector.tolist())


    def compute_state_values(self):
        pass
