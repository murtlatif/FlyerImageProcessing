import os.path
import pathlib


def apply_default_file_ext(file_path: str, default_file_ext: str, force: bool = False):
    """
    Appends the given default_file_ext to the file if it does not have
    a file extension already.

    Args:
        file_path (str): The file path to apply this function to
        default_file_ext (str): The extension to append if no extension was found.
        force (bool): If True, will overwrite the file extension
    Examples:
        >>> apply_default_file_ext('sample/file/path.txt', '.json')
        'sample/file/path.txt'
        >>> apply_default_file_ext('sample/file/path', '.json')
        'sample/file/path.json'
    """
    file_without_ext, file_ext = os.path.splitext(file_path)

    if file_ext == '' or force:
        file_path = file_without_ext + default_file_ext

    return file_path


def get_file_name_without_ext(file_path: str):
    """
    Returns the base file name without the extension.

    Args:
        file_path (str): The file path to get the file name from
    """
    file_name = os.path.basename(file_path)
    file_name_without_ext = os.path.splitext(file_name)[0]

    return file_name_without_ext


def create_directories_to_file(file_path: str):
    """
    Creates directories up to the given file path.
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)


def has_extension(file_path: str, valid_extensions: set[str]):
    """
    Checks if the file path contains an extension in the valid_extensions set.
    """
    file_extension = os.path.splitext(file_path)[1]
    return file_extension in valid_extensions
