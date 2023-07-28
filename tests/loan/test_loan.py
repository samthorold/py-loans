import pytest
from py_loans.loan import loan
from py_loans.process import ConstantValue


@pytest.mark.parametrize("payment,repayment_period", ((7, 25), (6, 25)))
def test_loan_length(payment: float, repayment_period: int) -> None:
    start_value = 100
    interest_rate_process = ConstantValue(value=0.05)
    payment_process = ConstantValue(value=payment)
    time_step = 0
    ln = loan(
        start_value=start_value,
        interest_rate_process=interest_rate_process,
        payment_process=payment_process,
        time_step=time_step,
        repayment_period=repayment_period,
    )

    repayment = list(ln)

    assert len(repayment) == repayment_period, repayment
