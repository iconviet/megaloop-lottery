from pprint import pprint
from random import random


def _weighted_random(weights: list) -> int:
    remaining_distance = random() * sum(weights)
    for i, w in enumerate(weights):
        remaining_distance -= w
        if remaining_distance < 0:
            return i


def sim():
    # As we see here,
    # item index 1 and 3 ( with probability 0.2 and 0.5 ) should always have highest count of being chosen
    weights = [0.1, 0.2, 0.05, 0.5, 0.05, 0.1]
    stats = {}
    for _ in range(10000):
        r = _weighted_random(weights)
        if r not in stats:
            stats[r] = 1
        else:
            stats[r] += 1
    pprint(stats)


if __name__ == '__main__':
    sim()
