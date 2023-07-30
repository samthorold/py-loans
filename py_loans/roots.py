"""Root finding algorithms for calculating payment amounts for a given loan term."""

from typing import Callable

from pydantic import BaseModel


class Root(BaseModel):
    """Result of a root-finding algorithm.

    Attributes:
        value: The root.
        iterations: How many iterations it took to find the root.
        converged: Did the algorithm converge?
        tol: The tolerance used to find the root.

    """

    value: float
    iterations: int
    converged: bool
    tol: float


def _same_sign(a: float, b: float) -> bool:
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
    max_iterations: int = 50,
) -> Root:
    """Bisection root-finding algorithm.

    Arguments:
        f: Objective function.
        a: Left of the initial search interval.
        b: Right of the initial search interval.
        tol: Maximum distance between a and b or value of `f((a+b)/2)`.
        max_iterations: Maximum iterations without convergence.

    Examples:
        >>> bisect(f=lambda x: x*x - 4, a=0, b=4, tol=0.001)
        Root(value=2.0, iterations=0, converged=True, tol=0.001)
        >>> root = bisect(
        ... f=lambda x: x*x*x + 8, a=-7, b=-1, tol=1e-25, max_iterations=100
        ... )
        >>> root.value
        -2.0
        >>> root.converged
        True

    """
    iteration = 0
    while iteration < max_iterations:
        c = (a + b) / 2
        if ((b - a) / 2) < tol or abs(fc := f(c)) < tol:
            return Root(value=c, iterations=iteration, converged=True, tol=tol)

        if _same_sign(f(a), fc):
            a = c
        else:
            b = c

        iteration += 1

    return Root(value=(a + b) / 2, iterations=iteration, converged=False, tol=tol)
