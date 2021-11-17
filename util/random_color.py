import numpy as np


def generate_random_color(grayscale: bool = False) -> tuple:
    """
    Generates a tuple containing 1 or 3 elements depending on if a grayscale
    color is generated, with each element being a random integer from 0-255.

    Args:
        grayscale (bool, optional): Whether the image is grayscale. Defaults to False.

    Returns:
        tuple: The randomly generated color
    """
    channels = 3
    if grayscale:
        channels = 1

    color = tuple(np.random.choice(range(256), size=channels))
    return color
