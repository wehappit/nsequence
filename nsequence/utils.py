def is_floating_integer(n: float) -> bool:
    """
    True if `n` is a float with just zeros after the decimal point
    """
    return n % 1 == 0


def count_integers_between(position1: int, position2: int) -> int:
    return abs(position2 - position1) + 1
