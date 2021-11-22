import numpy as np


def generate_random_color() -> tuple:
    """
    Generates a tuple containing 3 elements with each element being a
    random integer from 0-255.

    Returns:
        tuple: The randomly generated color
    """
    color = tuple(np.random.choice(range(256), size=3))
    return color
