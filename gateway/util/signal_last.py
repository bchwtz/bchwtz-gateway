from typing import Iterable, Any, Tuple

def signal_last(it:Iterable[Any]) -> Iterable[Tuple[bool, Any]]:
    """
    Checks if this is the last iteration of a for loop
    """
    iterable = iter(it)
    ret_var = next(iterable)
    for val in iterable:
        yield False, ret_var
        ret_var = val
    yield True, ret_var
