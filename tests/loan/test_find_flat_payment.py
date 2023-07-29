import pytest
from py_loans.loan import find_flat_payment
from py_loans.process import ConstantValue


@pytest.mark.parametrize(
    "repayment_period,interest_rate,expected", ((25, 0.0, 400), (25, 0.05, 710))
)
def test_find_flat_payment(
    repayment_period: int, interest_rate: float, expected: float
) -> None:
    start_value = 10000
    interest_rate_process = ConstantValue(value=interest_rate)
    time_step = 0
    tol = 5
    payment = find_flat_payment(
        start_value=start_value,
        interest_rate_process=interest_rate_process,
        time_step=time_step,
        repayment_period=repayment_period,
        a=0,
        b=100_000,
        tol=tol,
    )

    assert abs(payment - expected) <= tol, (payment, expected, tol)
