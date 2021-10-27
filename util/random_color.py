import numpy as np


def generate_random_color() -> str:
    color = tuple(np.random.choice(range(256), size=3))
    return color
