from collections import Counter
from typing import Generator


Roll = tuple[int, ...]


class Widget:

    def __init__(
        self,
        roll_values: dict[Roll, float],
        num_dice: int = 5,
        num_faces: int = 6,
        num_rolls: int = 3,
        keep_all_optimal: bool = False,
        use_dynamic_programming: bool = True,
    ):
        self.num_dice = num_dice
        self.num_faces = num_faces
        self.num_rolls = num_rolls
        self.keep_all_optimal = keep_all_optimal
        self.use_dynamic_programming = use_dynamic_programming

        self.roll_values = [{} for _ in range(self.num_rolls - 1)]
        self.roll_values.append(self._parse_roll_values(roll_values))
        self.optimal_moves = [{} for _ in range(self.num_rolls - 1)]

        self._compute_strategy_and_values()

    def _parse_roll_values(self, roll_values: dict[Roll, float]) -> dict[Roll, float]:
        parsed_roll_values = {}
        for roll, value in roll_values.items():
            roll = tuple(sorted(roll))
            pre_existing_value = parsed_roll_values.get(roll)
            if pre_existing_value is not None and pre_existing_value != value:
                raise ValueError(f"Inconsistent values for roll {roll}: {pre_existing_value} and {value}")
            parsed_roll_values[roll] = value

        for roll in iter_possible_rolls(self.num_dice, self.num_faces):
            if roll not in parsed_roll_values:
                raise ValueError(f"Roll missing in input roll_values: {roll}")

        return parsed_roll_values

    def _compute_strategy_and_values(self):
        for idx in range(self.num_rolls - 2, -1, -1):
            self.roll_values[idx], self.optimal_moves[idx] = self._compute_strategy_one_roll(self.roll_values[idx + 1])

    def _compute_strategy_one_roll(self, next_roll_values: dict[Roll, float]) -> tuple[
        dict[Roll, float], dict[Roll, list[Roll]]
    ]:
        values_given_kept = self._compute_values_given_kept(next_roll_values)
        return self._compute_from_conditional_values(values_given_kept)

    def _compute_values_given_kept(self, next_roll_values: dict[Roll, float]) -> dict[Roll, float]:
        values_given_kept = next_roll_values.copy()
        for num_kept in range(self.num_dice - 1, -1, -1):
            for kept in iter_possible_rolls(num_kept, self.num_faces):
                values_given_kept[kept] = sum(
                    values_given_kept[tuple(sorted(kept + (i,)))] for i in range(1, self.num_faces + 1)
                ) / self.num_faces

        return values_given_kept

    def _compute_from_conditional_values(self, values_given_kept: dict[Roll, float]) -> tuple[
        dict[Roll, float], dict[Roll, list[Roll]]
    ]:
        if self.use_dynamic_programming:
            return self._compute_from_cond_dp(values_given_kept)
        return self._compute_from_cond(values_given_kept)

    def _compute_from_cond_dp(self, values_given_kept: dict[Roll, float]) -> tuple[
        dict[Roll, float], dict[Roll, list[Roll]]
    ]:
        roll_values = {(): values_given_kept[()]}
        optimal_moves = {(): {()}}

        for num_kept in range(1, self.num_dice + 1):
            for kept in iter_possible_rolls(num_kept, self.num_faces):
                roll_values[kept] = values_given_kept[kept]
                optimal_moves[kept] = {kept}
            for prev_kept in iter_possible_rolls(num_kept - 1, self.num_faces):
                value = roll_values[prev_kept]
                moves = optimal_moves[prev_kept]
                for die in range(1, self.num_faces + 1):
                    kept = tuple(sorted(prev_kept + (die,)))
                    if value > roll_values[kept]:
                        roll_values[kept] = value
                        optimal_moves[kept] = moves
                    elif self.keep_all_optimal and value == roll_values[kept]:
                        optimal_moves[kept].update(moves)

        roll_values = {roll: value for roll, value in roll_values.items() if len(roll) == self.num_dice}
        optimal_moves = {roll: list(moves) for roll, moves in optimal_moves.items() if len(roll) == self.num_dice}

        return roll_values, optimal_moves

    def _compute_from_cond(self, values_given_kept: dict[Roll, float]) -> tuple[
        dict[Roll, float], dict[Roll, list[Roll]]
    ]:
        roll_values = {roll: values_given_kept[roll] for roll in iter_possible_rolls(self.num_dice, self.num_faces)}
        optimal_moves = {roll: [roll] for roll in iter_possible_rolls(self.num_dice, self.num_faces)}
        
        for num_kept in range(self.num_dice - 1, -1, -1):
            for kept in iter_possible_rolls(num_kept, self.num_faces):
                value = values_given_kept[kept]
                for other_dice in iter_possible_rolls(self.num_dice - num_kept, self.num_faces):
                    roll = tuple(sorted(kept + other_dice))
                    if value > roll_values[roll]:
                        roll_values[roll] = value
                        optimal_moves[roll] = [kept]
                    elif self.keep_all_optimal and value == roll_values[roll]:
                        optimal_moves[roll].append(kept)

        return roll_values, optimal_moves


def iter_possible_rolls(num_dice: int, num_faces: int) -> Generator[Roll, None, None]:
    if num_dice == 0:
        yield ()
        return

    roll = [1 for _ in range(num_dice)]
    yield tuple(roll)
    while any(face_value != num_faces for face_value in roll):
        for idx_to_increment, face_value in reversed(list(enumerate(roll))):
            if face_value != num_faces:
                break
        else:
            assert False, "Logic error"
        roll[idx_to_increment] = face_value + 1
        for idx in range(idx_to_increment + 1, len(roll)):
            roll[idx] = roll[idx_to_increment]

        yield tuple(roll)


def is_subroll(subroll: Roll, roll: Roll) -> bool:
    return Counter(subroll) <= Counter(roll)
