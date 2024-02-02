identity = lambda x: x

# Some functions
_Fn = lambda x: x
_In = lambda x: x


def i_x(x):
    """Identity function"""
    return x


def l_x(x):
    """Linear function"""
    return 11 * x - 18


def q_x(x):
    """Quartic function"""
    return x**4 + 9


def a_x(x):
    """Absolute function"""
    return abs(x - 20)


def c_x(x):
    """Cubic function"""
    return x**3 - x**2 - 1


def h_x(x):
    """
    Harmonic function
    """
    return 1 / x
