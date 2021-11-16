import json
from dataclasses import asdict

from util.file_path_util import apply_default_file_ext

from .flyer_types import Flyer


def marshal_flyer(flyer: Flyer, file_path: str):
    """
    Convert the given flyer into a JSON, and save that to the given file
    path.

    Args:
        flyer (Flyer): The flyer object to marshal
        file_path (str): The file path to save the JSON file to
    """
    file_path = apply_default_file_ext(file_path, '.json')

    with open(file_path, 'w') as json_file:
        flyer_as_dict = asdict(flyer)
        json.dump(flyer_as_dict, json_file, indent=2)
