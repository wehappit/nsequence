

def i_x(x):
    """i_x function"""
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

def s_x(x):
    """Sextique function"""
    # x(x−1)(x−2)(x−3)(x−4)(x-5)
    return x**6 - 10*(x**5) + 35*(x**4) - 50*(x**3) + 24*(x**2)
