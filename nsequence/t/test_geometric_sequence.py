import contextlib


def is_integer(value: float) -> bool:

    res = None

    with contextlib.suppress(TypeError) as exc:
        res = value % 1 == 0
        return bool(res or exc)

    return bool(res)


print(is_integer(1))
