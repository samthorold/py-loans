from py_loans.roots import bisect


def test_bisect() -> None:
    def objective_func(x: float) -> float:
        return x * x - 4

    a = 0
    b = 4
    tol = 1e-4
    max_iterations = 20
    expected = 2

    root = bisect(f=objective_func, a=a, b=b, tol=tol, max_iterations=max_iterations)

    assert abs(root.value - expected) < tol, root
    assert root.iterations == 0, root
