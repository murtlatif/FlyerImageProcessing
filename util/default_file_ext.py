import os.path


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
