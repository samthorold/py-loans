from typing import Callable

from pydantic import BaseModel


class Root(BaseModel):
    value: float
    iterations: int
    converged: bool
    tol: float


def same_sign(a: float, b: float) -> bool:
    """
    Examples:

    >>> same_sign(1, 1)
    True
    >>> same_sign(1, -1)
    False
    >>> same_sign(-1, -1)
    True
    """
    if a > 0 and b > 0:
        return True
    if a < 0 and b < 0:
        return True
    return False


def bisect(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float,
    max_iterations: int = 20,
) -> Root:
    iteration = 0
    while iteration < max_iterations:
        c = (a + b) / 2
        if ((b - a) / 2) < tol or abs(fc := f(c)) < tol:
            return Root(value=c, iterations=iteration, converged=True, tol=tol)

        if same_sign(f(a), fc):
            a = c
        else:
            b = c

        iteration += 1

    return Root(value=(a + b) / 2, iterations=iteration, converged=False, tol=tol)
