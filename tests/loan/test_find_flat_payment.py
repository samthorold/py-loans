import pytest
from py_loans.loan import find_flat_payment
from py_loans.process import ConstantValue


@pytest.mark.parametrize("repayment_period", (25, 25))
def test_find_flat_payment(repayment_period: int) -> None:
    start_value = 10000
    interest_rate_process = ConstantValue(value=0.0)
    time_step = 0
    repayment_gen = find_flat_payment(
        start_value=start_value,
        interest_rate_process=interest_rate_process,
        time_step=time_step,
        repayment_period=repayment_period,
    )

    repayment = list(repayment_gen)

    assert repayment[-1].payment == start_value / repayment_period, repayment[-1]
