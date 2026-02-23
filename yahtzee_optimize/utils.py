from collections import Counter
from typing import Generator

Roll = tuple[int, ...]


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
