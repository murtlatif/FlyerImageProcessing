from typing import TypeVar

T = TypeVar('T')


def string_to_float_safe(string: 'str | None', display_error: bool = True) -> 'float | None':
    """
    Converts a string to a float value. If the conversion could not be
    made, returns None instead.
    """
    if string is None:
        return None

    value = None
    try:
        value = float(string)
    except ValueError:
        if display_error:
            print(f'Failed to convert string "{string}" to float.')

    return value


def string_to_int_safe(string: 'str | None', display_error: bool = True) -> 'int | None':
    """
    Converts a string to an int value. If the conversion could not be
    made, returns None instead.
    """
    if string is None:
        return None

    value: int = None
    try:
        value = int(string)
    except ValueError:
        if display_error:
            print(f'Failed to convert string "{string}" to int.')

    return value


def string_to_any_safe(string: 'str | None', target: T, display_error: bool = True) -> 'T | None':
    """
    Converts a string to a given type. If the conversion could not be
    made, returns None instead.
    """
    if string is None:
        return None

    value: T = None
    try:
        value = target(string)
    except ValueError:
        if display_error:
            print(f'Failed to convert string "{string}" to target: "{target}".')

    return value
